#! /usr/bin/python
#############################################
# Prueba potes
# ============
#
# Description :
#  Prueba para recibir del arduino, los valores 
#  de los potes
#  
# Author :
#  Hugo Arboleas <harboleas@citedef.gob.ar>
#
#############################################

import struct
import serial
import time

# Reset del Arduino para una conexion limpia
arduino = serial.Serial("/dev/ttyUSB0")
arduino.setDTR(False)
time.sleep(1)
arduino.flushInput()
arduino.setDTR(True)
arduino.close()

arduino = serial.Serial("/dev/ttyUSB0", 115200)

time.sleep(10)

def read_pote() :

    datos = arduino.read(2)
    return struct.unpack("h", datos)[0]  # convierte 2 bytes a int

while True :

    arduino.write("a")
    p1 = read_pote()
    p2 = read_pote()
    p3 = read_pote()
    
    print p1, p2, p3

#  vim: set ts=8 sw=4 tw=0 et :
