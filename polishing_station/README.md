You need to update the buffer size in the Ardiuno library before running this script.

In the lab environment, I modified the line 53 of 
```
/home/sf3202msi/.arduino15/packages/arduino/hardware/avr/1.8.6/cores/arduino/HardwareSerial.h
```
into
```
#define SERIAL_RX_BUFFER_SIZE 256
```

Read [Arduino IDE 2.0.3 Serail RX Buffer Modified?](https://forum.arduino.cc/t/arduino-ide-2-0-3-serail-rx-buffer-modified/1067240) for more information.
