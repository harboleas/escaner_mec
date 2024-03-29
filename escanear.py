##############################################################################
# Macro para escanear
# ===================
#
# Description :
#  Recibe del Arduino los valores de los potes 
#  y modifica, segun estos datos, la posicion 
#  del modelo 3d del escaner en el FreeCAD. 
#  Ademas genera un archivo .xyz con las coordenadas 
#  de los puntos registrados por el escaner
#
# Author :
#  Hugo Arboleas <harboleas@citedef.gob.ar>
#
##############################################################################
# 
# Copyright 2016 Hugo Arboleas
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
import FreeCAD
from PySide2 import QtGui, QtCore, QtWidgets
import struct
import serial
import time
import math
import Draft

class Escaner_Dialog(QtWidgets.QDialog):

    def __init__(self):
        super().__init__()

        self.RADIANES_POR_CUENTA = math.radians(66) / (552.0 - 257.0)

        doc = FreeCAD.ActiveDocument

        # Creo 3 objetos Placement para las rotaciones
        self.rot1 = FreeCAD.Placement()
        self.rot2 = FreeCAD.Placement()
        self.rot3 = FreeCAD.Placement()

        # Partes moviles del escaner
        self.acople = doc.Body001
        self.pote2 = doc.Part__Feature002
        self.tuerca2 = doc.Part__Feature003
        self.brazo1 = doc.Body002
        self.pote3 = doc.Part__Feature004
        self.tuerca3 = doc.Part__Feature005
        self.brazo2 = doc.Body003

        self.partes_rot1 = [self.acople, self.pote2, self.tuerca2, self.brazo1, self.pote3, self.tuerca3, self.brazo2]

        self.orig = [parte.Placement.copy() for parte in self.partes_rot1]

        self.partes_rot2 = self.partes_rot1[3:]
        self.partes_rot3 = self.partes_rot2[3:]


        self.rot1.Rotation.Axis = FreeCAD.Vector(0,0,1)

        self.punto_orig = FreeCAD.Vector(0, -49.4, 3.9)

        self.puntos = []

        # Reset del Arduino para una conexion limpia
        self.arduino = serial.Serial("/dev/ttyUSB0")
        self.arduino.setDTR(False)
        time.sleep(1)
        self.arduino.flushInput()
        self.arduino.setDTR(True)
        self.arduino.close()

        self.arduino = serial.Serial("/dev/ttyUSB0", 115200)

        self.arduino.read(1)  # espera que el arduino este listo

        # Actualiza los datos cada 15 ms
        self.timer = QtCore.QTimer()
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.update_escaner)
        self.timer.start(15)

        # Propiedades de la ventana        
        self.setGeometry(250, 250, 500, 250)
        self.setWindowTitle("Escaner 3D mecanico")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.label_autor = QtWidgets.QLabel("Hugo Arboleas <harboleas@citedef.gob.ar>" , self)
        self.label_autor.move(20, 225)


        self.label_potes = QtWidgets.QLabel("Cuentas potes : 0, 0, 0                   " , self)
        self.label_potes.move(20, 20)

        self.label_punto = QtWidgets.QLabel("Coord punto : 0, 0, 0                                                      " , self)
        self.label_punto.move(20, 60)

        self.okButton = QtWidgets.QPushButton("OK", self)
        self.okButton.clicked.connect(self.onOk)
        self.okButton.move(260, 180)

        self.tomar_coord_button = QtWidgets.QPushButton("Tomar punto", self)
        self.tomar_coord_button.clicked.connect(self.tomar_coord)
        self.tomar_coord_button.move(20, 180)

        self.adquirir = QtWidgets.QCheckBox("Adquirir puntos", self)
        self.adquirir.move(20, 100)

        self.punto = None
        self.show()

    def read_pote(self):

        datos = self.arduino.read(2)
        return struct.unpack("h", datos)[0]  # convierte 2 bytes a int

    def update_escaner(self):
        "Actualiza el modelo segun los datos leidos"

        self.arduino.write(b"a") # pide los datos al arduino

        K = self.RADIANES_POR_CUENTA

        # Lee el valor de los potes y lo convierte a radianes
        p1 = self.read_pote()
        p3 = self.read_pote()
        p2 = self.read_pote()

        potes = "Cuentas potes : %d, %d, %d" % (p1, p2, p3)
        self.label_potes.setText(potes)

        offset1 = math.radians(0)
        offset2 = - math.radians(55)
        offset3 = - math.radians(50)
        self.update_pos(p1*K + offset1, p2*K + offset2, p3*K + offset3)

        coord_punto = "Coord punto : %f, %f, %f" % (self.punto.x, self.punto.y, self.punto.z)
        self.label_punto.setText(coord_punto)

        if self.adquirir.isChecked():
            self.puntos.append(self.punto)

    def tomar_coord(self):

        Draft.makePoint(self.punto)
        print(self.punto)
        self.puntos.append(self.punto)

    def onOk(self):

        self.timer.stop()
        self.arduino.close()
#        if self.puntos:
#            aux = self.puntos[1:]
#            aux.append(self.puntos[0])
#            pares = zip(self.puntos, aux)
#            for a,b in pares:
#                Draft.makeLine(a, b)

        a = open("/home/nan/puntos.xyz", "w")

        for p in self.puntos:
            a.write("%f %f %f\n" % (p.x, p.y, p.z))

        a.close()

        # Restablece el modelo 3D a su posicion original
        for parte, orig in zip(self.partes_rot1, self.orig):
            parte.Placement = orig

        self.close()

    def update_pos(self, ang1, ang2, ang3):

        # Rotacion pote 1
        self.rot1.Rotation.Angle = ang1

        for parte, orig in zip(self.partes_rot1, self.orig):
            parte.Placement = self.rot1.multiply(orig)

        punto = self.rot1.multVec(self.punto_orig)

        # Rotacion pote 2
        z = FreeCAD.Vector(0,0,1)
        self.rot2.Rotation.Axis = self.pote2.Placement.Rotation.multVec(z)
        self.rot2.Rotation.Angle = ang2
        self.rot2.Base = self.pote2.Placement.Base
        despl = self.rot2.Base.negative()

        for parte in self.partes_rot2:
            parte.Placement.move(despl)
            parte.Placement = self.rot2.multiply(parte.Placement)

        punto = punto.add(despl)
        punto = self.rot2.multVec(punto)

        # Rotacion pote 3
        self.rot3.Rotation.Axis = self.pote3.Placement.Rotation.multVec(z)
        self.rot3.Rotation.Angle = ang3
        self.rot3.Base = self.pote3.Placement.Base
        despl = self.rot3.Base.negative()

        for parte in self.partes_rot3:
            parte.Placement.move(despl)
            parte.Placement = self.rot3.multiply(parte.Placement)

        punto = punto.add(despl)
        punto = self.rot3.multVec(punto)
        self.punto = punto

###########################################################################################

form = Escaner_Dialog()


#  vim: set ts=8 sw=4 tw=0 et :
