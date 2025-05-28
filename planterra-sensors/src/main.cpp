#include <Arduino.h>
#include <Wire.h>

void I2C_onRequest()
{
  uint8_t data_addr = Wire.read(); // Read the data_addr address from the master
  int analogValue = analogRead(data_addr + 14);
  Wire.write((uint8_t)(analogValue >> 8));
  Wire.write((uint8_t)(analogValue & 0xFF));
}

void setup()
{
  // put your setup code here, to run once:
  Serial.begin(9600);
  Wire.begin(0x01);   // Initialize I2C communication
  pinMode(A0, INPUT); // Set pin A0 as input
  pinMode(A1, INPUT); // Set pin A1 as input
  pinMode(A2, INPUT); // Set pin A2 as input
  pinMode(A3, INPUT); // Set pin A3 as input
  pinMode(A4, INPUT); // Set pin A4 as input
  pinMode(A5, INPUT); // Set pin A5 as input
}

void loop()
{
  // put your main code here, to run repeatedly:
}
