const char pulsePin0 = 2;
const char pulsePin1 = 5;
const char directPin0 = 3;
const char directPin1 = 6;
const int swPin0 = 8;
const int swPin1 = 9;

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
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(pulsePin0, OUTPUT);
  pinMode(pulsePin1, OUTPUT);
  pinMode(directPin0, OUTPUT);
  pinMode(directPin1, OUTPUT);
  pinMode(swPin0, INPUT_PULLUP);
  pinMode(swPin1, INPUT_PULLUP);
}

void loop() {
  // put your main code here, to run repeatedly:
  while (!Serial) {
    continue;
  }
  char directMotor0 = readChar();
  char directMotor1 = readChar();
  int numPulseMotor0 = readShort();
  int numPulseMotor1 = readShort();
  if (directMotor0 == 2) {
    resetPosition();
    Serial.println("Reset done");
  } else {
    setOneDirect(0, directMotor0);
    setOneDirect(1, directMotor1);
    sendPulses(numPulseMotor0, numPulseMotor1);
    Serial.println("[" + String((int)directMotor0) + ", " + String((int)directMotor1) + ", " 
            + String(numPulseMotor0) + ", " + String(numPulseMotor1) + "]");
  }
}
