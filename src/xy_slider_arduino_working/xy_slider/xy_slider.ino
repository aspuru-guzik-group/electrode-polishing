const char pulsePin0 = 2;
const char pulsePin1 = 5;
const char directPin0 = 3;
const char directPin1 = 6;

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
  long delayPulse0 = 1000000 / numPulse0 - 10;
  long delayPulse1 = 1000000 / numPulse1 - 10;
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
  switch (directPin) {
    case 0:
      digitalWrite(directPin0, level);
      break;
    case 1:
      digitalWrite(directPin1, level);
      break;
    default:
      break;
  }
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(pulsePin0, OUTPUT);
  pinMode(pulsePin1, OUTPUT);
  pinMode(directPin0, OUTPUT);
  pinMode(directPin1, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  while (!Serial) {
    continue;
  }
  char directMotor0 = readChar();
  char directMotor1 = readChar();
  setOneDirect(0, directMotor0);
  setOneDirect(1, directMotor1);
  int numPulseMotor0 = readShort();
  int numPulseMotor1 = readShort();
  sendPulses(numPulseMotor0, numPulseMotor1);  
  Serial.write(0x00);
}
