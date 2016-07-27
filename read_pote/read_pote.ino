///////////////////////////////////////////////////////////////////////////////
// Read pote
// =========
//
// Description :
//  Lee el valor de los potenciometros del escaner y los envia a la PC.
//
// Author :
//  Hugo Arboleas <harboleas@citedef.gob.ar>
//
//////////////////////////////////////////////////////////////////////////////
//
// Copyright 2016 Hugo Arboleas
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
//////////////////////////////////////////////////////////////////////////////

#define P1 7
#define P2 6
#define P3 5

int aux;

union byte_int
{
    byte data[2];
    int val;
} pote1, pote2, pote3; // Valor de los potes

void setup()
{

    Serial.begin(115200);

    Serial.write(1);  // Envia un byte para avisar que ya esta listo

}

void loop()
{
    
    // Lectura de los potenciometros
    pote1.val = analogRead(P1);
    pote2.val = analogRead(P2);
    pote3.val = analogRead(P3);
   
    // Tx de los valores a la PC

    // Espera la lectura de un byte para enviar
    while(!Serial.available());
    
    aux = Serial.read(); 
    
    Serial.write(pote1.data, 2);
    Serial.write(pote2.data, 2);
    Serial.write(pote3.data, 2);

}
  
/* vim: set ts=8 sw=4 tw=0 et :*/
