///////////////////////////////////////////////
// Read pote
// =========
//
// Description :
//  Lee el valor de los potenciometros del scanner y los envia
//  a la PC.
//
// Author :
//  Hugo Arboleas <harboleas@citedef.gob.ar>
//
///////////////////////////////////////////////

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
