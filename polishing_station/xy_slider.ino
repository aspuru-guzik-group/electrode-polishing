const unsigned long minUsDelay = 400; //minimum delay between motor pulses (us)

const int inputSize = SERIAL_RX_BUFFER_SIZE - 4; //WARNING! Ideally change HardwareSerial.h to have #define SERIAL_RX_BUFFER_SIZE 256 and this number must be multiple of 4
byte inputBytes[inputSize+2];

const char pulsePinX = 2; //x
const char pulsePinY = 5; //y
const char directPinX = 3;
const char directPinY = 6;
const int swPinX = 8;
const int swPinY = 9;

char jobType;
int16_t temp = 0;
unsigned long xCount = 0;
unsigned long yCount = 0;
int xDir = 0;
int yDir = 0;
unsigned long xDelay = 0;
unsigned long yDelay = 0;
unsigned long runTime = 0;
unsigned long nowMicros = 0;
unsigned long xLastMicros = 0;
unsigned long yLastMicros = 0;
unsigned long deltaMicros = 0;

void sendOnePulse(char pulsePin) {
      digitalWrite(pulsePin, LOW);
      digitalWrite(pulsePin, HIGH);
}

void resetPosition() {
  delayMicroseconds(minUsDelay); //ensure min time from the last pulse
  
  char xEnd = digitalRead(swPinX);
  char yEnd = digitalRead(swPinY);
  unsigned long xHomeCount = 10000;
  unsigned long yHomeCount = 10000;
  bool cont = true;
  while (cont) {
    cont = false;
    if (xEnd == HIGH) {
      digitalWrite(directPinX, HIGH);
      sendOnePulse(pulsePinX);
      xEnd = digitalRead(swPinX);
      cont = true;
    }
    else if (xHomeCount > 0) {
      digitalWrite(directPinX, LOW);
      sendOnePulse(pulsePinX);
      xHomeCount--;
      cont = true;
    }
    
    if (yEnd == HIGH) {
      digitalWrite(directPinY, HIGH);
      sendOnePulse(pulsePinY);
      yEnd = digitalRead(swPinY);
      cont = true;
    }
    else if (yHomeCount > 0) {
      digitalWrite(directPinY, LOW);
      sendOnePulse(pulsePinY);
      yHomeCount--;
      cont = true;
    }
    
    delayMicroseconds(minUsDelay);
  }
}

void takeSteps() {
  //Loop over each pulse until there are no steps neither for x nor for y
  while (xCount + yCount > 0) {
    nowMicros = micros();
    //check if motor x's time has come to pulse and if there are steps to be taken
    if ((xCount > 0) && (nowMicros - xLastMicros > xDelay)) {
      sendOnePulse(pulsePinX);
      xCount--;
      //Serial.println(xCount);
      xLastMicros = nowMicros;
    }
    //check if motor y's time has come to pulse and if there are steps to be taken
    if ((yCount > 0) && (nowMicros - yLastMicros > yDelay)) {
      sendOnePulse(pulsePinY);
      yCount--;
      yLastMicros = nowMicros;
    }
  }
}

void processBatch() {
  //read 4 bytes at a time from the buffer
  //the first 2 bytes are for 16 bit signed int for x, the remaining 2 bytes are for y
  //The sign is used for setting direction
 
  //ensure the first movement of the batch is started immediately by setting the start time very back.
  //assuming the delay is not more than 30mins
  nowMicros = micros();
  xLastMicros = nowMicros - 2147483646L; //roughly 30 mins (15bits of microseconds)
  yLastMicros = xLastMicros;
  
  for (int i = 0; i<inputSize-3; i=i+4) {
    //for each command in the batch
    temp = * (int16_t *) &inputBytes[i]; //the first 2 bytes
    xDir = (temp > 0);
    xCount = abs(temp);
    
    temp = * (int16_t *) &inputBytes[i+2]; //the next 2 bytes
    yDir = (temp > 0);
    yCount = abs(temp);
    
    //if x has more steps, set the total time by it (step count * minUsDelay), otherwise do the same for y
    if (xCount > yCount) {
      runTime = (xCount - 1) * minUsDelay; //minus one be
      xDelay = minUsDelay;
      yDelay = runTime / yCount; //integer division rounds towards 0
    }
    else {
      runTime = (yCount - 1) * minUsDelay;
      yDelay = minUsDelay;
      xDelay = runTime / xCount;
    }

    digitalWrite(directPinX, xDir);
    digitalWrite(directPinY, yDir);
    
    //Ensure we take the first step as soon as possible
    //for both X and Y
    //but not sooner than minUsDelay
    nowMicros = micros();

    //for X
    deltaMicros = nowMicros - xLastMicros;
    if (deltaMicros < minUsDelay) {
    	xLastMicros = (nowMicros - xDelay - 1) + (minUsDelay - deltaMicros);
    } 
    else {
      xLastMicros = (nowMicros - xDelay - 1);
    }
    //for Y
    deltaMicros = nowMicros - yLastMicros;
    if (deltaMicros < minUsDelay) {
      yLastMicros = (nowMicros - yDelay - 1) + (minUsDelay - deltaMicros);
    }
    else {
      yLastMicros = (nowMicros - yDelay - 1);
    }
    //Start moving
    takeSteps();
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(pulsePinX, OUTPUT);
  pinMode(pulsePinY, OUTPUT);
  pinMode(directPinX, OUTPUT);
  pinMode(directPinY, OUTPUT);
  pinMode(swPinX, INPUT_PULLUP);
  pinMode(swPinY, INPUT_PULLUP);
  digitalWrite(pulsePinX, LOW);
  digitalWrite(pulsePinY, LOW);
  Serial.println("Ready");
}

void loop() {
  if (Serial.available() > 0) {
    jobType = Serial.read();
    switch (jobType) {
      case 'R': //R for resetting-homing
        resetPosition();
        Serial.println("Homing Completed");
        break;
      case 'M': //M for movement
        while (Serial.available() < inputSize){}
        Serial.readBytes(inputBytes,inputSize);
        processBatch();
        Serial.println("Batch Completed");
        break;
      default: //unknown message
        Serial.println("Unknown command received.");
        break; 
    }
  }
}
