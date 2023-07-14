#include <Wire.h>
#include "Adafruit_VL6180X.h"

const char pulsePin0 = 2;
const char pulsePin1 = 5;
const char directPin0 = 3;
const char directPin1 = 6;
const int swPin0 = 8;
const int swPin1 = 9;
const char distPin0 = 12;
const char distPin1 = 13;
const char resistancePin = A0;

Adafruit_VL6180X lox = Adafruit_VL6180X();

int readShort() {
  // Read a short int from serial port, big endian. 
  // Wait until two bytes from serial port
  while (Serial.available() <= 1) {
    continue;
  }
  // Read two bytes, assign to an int
  unsigned char highByte = Serial.read();
  unsigned char lowByte = Serial.read();
  int a = highByte << 8 | lowByte;
  return a;  
}

char readChar() {
  while (Serial.available() < 1) {
    continue;
  }
  char a = Serial.read();
  return a;
}

void writeShort(short int num) {
  unsigned char upperByte = (num >> 8) & 0xFF;
  unsigned char lowerByte = num & 0xFF;
  Serial.write(upperByte);
  Serial.write(lowerByte);
}

char readDistance() {
  char dev;
  char addr;
  char status;
  char dist;

  // set both status pin to LOW = not active
  digitalWrite(distPin0, LOW);
  digitalWrite(distPin1, LOW);
  
  // wait for input from serial, then choose which device to read from
  // while (!Serial.available()) {
  //   continue;
  // }
  // dev = Serial.read();
  dev = readChar();
  switch (dev) {
    case 0:
      // read distance0, if device failure return 0xff
      digitalWrite(distPin0, HIGH);
      digitalWrite(distPin1, LOW);
      delay(10);
      if (lox.begin() == 0) {
        return 0xff;
      }
      break;
    case 1:
      // read disntance1, if device failure return 0xfe
      digitalWrite(distPin0, LOW);
      digitalWrite(distPin1, HIGH);
      delay(10);
      if (lox.begin() == 0) {
        return 0xfe;
      }
      break;
    default:
      digitalWrite(distPin0, LOW);
      digitalWrite(distPin1, LOW);
      delay(10);
      break;
  }

  // read address and status of device
  addr = lox.getAddress();
  delay(10);
  status = lox.readRangeStatus();
  delay(10);

  // default device is 0x29 if not return 0xfd
  if (addr != 0x29) {
    return 0xfd;
  }
  // if device status is not 0x00, then device error, return 0xfc
  if (status != 0x00) {
    return 0xfc;
  }
  
  // clear register in distance dev, read distance in mm, return
  lox.readRangeResult();
  dist = lox.readRange();
  return dist;
}

int readVoltage() {
  int val = analogRead(resistancePin);
  return val;
}

void sendOnePulse(char pulsePin) {
  switch (pulsePin) {
    case 0:
      digitalWrite(pulsePin0, LOW);
      digitalWrite(pulsePin0, HIGH);
      delayMicroseconds(5);
      digitalWrite(pulsePin0, LOW);
      delayMicroseconds(5);
      break;
    case 1:
      digitalWrite(pulsePin1, LOW);
      digitalWrite(pulsePin1, HIGH);
      delayMicroseconds(5);
      digitalWrite(pulsePin1, LOW);
      delayMicroseconds(5);
      break;
    default:
      break;
  }
}

void sendPulses(int numPulse0, int numPulse1) {
  int countPulse0 = 0;
  int countPulse1 = 0;
  long delayPulse0 = 100000 / numPulse0 - 10;
  long delayPulse1 = 100000 / numPulse1 - 10;
  while (countPulse0 < numPulse0 || countPulse1 < numPulse1) {
    long timing0 = countPulse0 * (delayPulse0 + 10);
    long timing1 = countPulse1 * (delayPulse1 + 10) +20;
    if (timing0 + delayPulse0 < timing1) {
      // If next pulse timing0 is less than timing1, send pulse0 and wait for delay between timing0s then next pulse0
      sendOnePulse(0);
      int deltaTime = delayPulse0;
      delayMicroseconds(deltaTime);
      countPulse0 += 1;
    }
    else if (timing0 <= timing1) {
      // If pulse timing0 is less than timing1, send pulse0 and wait for timing1 - timing0 then pulse1
      sendOnePulse(0);
      int deltaTime = timing1 - timing0;
      delayMicroseconds(deltaTime);
      countPulse0 += 1;
    }
    else if (timing1 + delayPulse1 < timing0) {
      // If next pulse timing1 is less than timing0, send pulse1 and wait for delay between timing1s then next pulse1
      sendOnePulse(1);
      int deltaTime = delayPulse1;
      delayMicroseconds(deltaTime);
      countPulse1 += 1;
    }
    else {
      // Other cases send pulse1 and wait for timing0 - timing1 then pulse0
      sendOnePulse(1);
      int deltaTime = timing0 - timing1;
      delayMicroseconds(deltaTime);
      countPulse1 += 1;
    }
  }
}

void setOneDirect(char directPin, char level) {
  if (directPin == 0) {
    digitalWrite(directPin0, level);
  } else if (directPin == 1) {
    digitalWrite(directPin1, level);
  }
  delayMicroseconds(10);
}

void moveTwoSliders() {
  while (Serial.available() < 6) {
    continue;
  }
  char directMotor0 = readChar();
  char directMotor1 = readChar();
  int numPulseMotor0 = readShort();
  int numPulseMotor1 = readShort();
  setOneDirect(0, directMotor0);
  setOneDirect(1, directMotor1);
  sendPulses(numPulseMotor0, numPulseMotor1);
  Serial.write(0x00);
}

void resetPosition() {
  // Go left until switch is pushed
  setOneDirect(1, HIGH);
  while (digitalRead(swPin1) == HIGH) {
    sendOnePulse(1);
    delayMicroseconds(1000);
  }
  // Go to the origin
  setOneDirect(1, LOW);
  for (int i=0; i<10000; i++) {
    sendOnePulse(1);
    delayMicroseconds(1000);
  }

  // Go down until switch is pushed
  setOneDirect(0, HIGH);
  while (digitalRead(swPin0) == HIGH) {
    sendOnePulse(0);
    delayMicroseconds(1000);
  }
  // Go to the origin
  setOneDirect(0, LOW);
  for (int i=0; i<10000; i++) {
    sendOnePulse(0);
    delayMicroseconds(1000);
  }
  Serial.write(0x00);
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(distPin0, OUTPUT);
  pinMode(distPin1, OUTPUT);
  pinMode(pulsePin0, OUTPUT);
  pinMode(pulsePin1, OUTPUT);
  pinMode(directPin0, OUTPUT);
  pinMode(directPin1, OUTPUT);
  pinMode(swPin0, INPUT_PULLUP);
  pinMode(swPin1, INPUT_PULLUP);
}

void loop() {
  // put your main code here, to run repeatedly:
  char funcCode;

  // wait for bytes in inStream of serial port
  while (!Serial.available()) {
    continue;
  }

  // read the function code, then use function
  funcCode = Serial.read();
  switch (funcCode) {
    case 0x00: {
      // self checking
      Serial.write(0x00);
      break;
    }
    case 0x01:{
      // move slider
      // Serial.write(0x01);
      moveTwoSliders();
      break;
    }

    case 0x02: {
      resetPosition();
      break;
    }

    case 0x05: {
      // read distance in mm, need one more follow-up byte to determine sensor 0/1
      // range [0x00, 0xef], 0xf_ is error message
      char dist = readDistance();
      Serial.write(dist);
      break;
    }

    case 0x06: {
      // Serial.write(0x06);
      int voltage = readVoltage();
      writeShort(voltage);
      break;
    }

    default:
      Serial.write(0xff);
      break;
  }
}
