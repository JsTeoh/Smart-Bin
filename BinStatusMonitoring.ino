#include <Wire.h>
#include <arduinoUtils.h>
#include <arduinoLoRa.h>
#include <SPI.h>
#include <TinyGPS++.h>
#include <SoftwareSerial.h>

static const int RXPin = 4, TXPin = 3;
static const uint32_t GPSBaud = 9600;

// The TinyGPS++ object
TinyGPSPlus gps;

// Serial connection to the GPS device
SoftwareSerial ss(RXPin, TXPin);
int e;
char clat[11];
char clng[11];
char msgToLora[50];

//Ultrasonic Sensor
int trigPin = 6;    // Trigger
int echoPin = 7;    // Echo
long duration;
long distance;
long UltrasonicSensorDis;

void setup()
{
  // Open serial communications and wait for port to open:
  Serial.begin(9600);
  //LoRa Setup
  LoraSetup();
  //GPS Baud Rate
  ss.begin(GPSBaud);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
}

void loop()
{
    while (ss.available() > 0)
    if (gps.encode(ss.read()))
    {
      
    // Get GPS coordinates
    displayInfo();
    double dlat = gps.location.lat();
    dtostrf(dlat,sizeof(dlat),6,clat);
    double dlng = gps.location.lng();
    dtostrf(dlng,sizeof(dlat),6,clng);

    // Get fill level of bin
    UltrasonicSensor(trigPin,echoPin);
    UltrasonicSensorDis = distance;

    //Send packet to LoRa gateway every 10 seconds
    sprintf(msgToLora,"Location: %s,%s\r\nDate: %i/%i/%i\r\nTime: %i:%i:%i\r\nFill Level: %i cm",clat,clng,gps.date.month(),gps.date.day(),gps.date.year(),gps.time.hour(),gps.time.minute(),gps.time.second(),UltrasonicSensorDis);
    
    e = sx1272.sendPacketTimeout(0, msgToLora);
    Serial.print(F("Packet sent, state "));
    Serial.println(e, DEC);
    delay(10000);
    }
}

void LoraSetup()
{
  // Print a start message
  Serial.println(F("SX1272 module and Arduino: send packets without ACK"));
  // Power ON the module
  e = sx1272.ON();
  Serial.print(F("Setting power ON: state "));
  Serial.println(e, DEC);
  // Set transmission mode and print the result
  e |= sx1272.setMode(4);
  Serial.print(F("Setting Mode: state "));
  Serial.println(e, DEC);
  // Set header
  e |= sx1272.setHeaderON();
  Serial.print(F("Setting Header ON: state "));
  Serial.println(e, DEC);
  // Select frequency channel
  e |= sx1272.setChannel(CH_01_900);
  Serial.print(F("Setting Channel: state "));
  Serial.println(e, DEC);
  // Set CRC
  e |= sx1272.setCRC_ON();
  Serial.print(F("Setting CRC ON: state "));
  Serial.println(e, DEC);
  // Select output power (Max, High or Low)
  e |= sx1272.setPower('H');
  Serial.print(F("Setting Power: state "));
  Serial.println(e, DEC);
  // Set the node address and print the result
  e |= sx1272.setNodeAddress(3);
  Serial.print(F("Setting node address: state "));
  Serial.println(e, DEC);
  // Print a success message
  if (e == 0)
    Serial.println(F("SX1272 successfully configured"));
  else
    Serial.println(F("SX1272 initialization failed"));
}

void displayInfo()
{
  Serial.print(F("Location: ")); 
  if (gps.location.isValid())
  {
    Serial.print(gps.location.lat(), 6);
    Serial.print(F(","));
    Serial.print(gps.location.lng(), 6);
  }
  else
  {
    Serial.print(F("INVALID"));
  }
  Serial.print(F("  Date/Time: "));
  if (gps.date.isValid())
  {
    Serial.print(gps.date.month());
    Serial.print(F("/"));
    Serial.print(gps.date.day());
    Serial.print(F("/"));
    Serial.print(gps.date.year());
  }
  else
  {
    Serial.print(F("INVALID"));
  }
  Serial.print(F(" "));
  if (gps.time.isValid())
  {
    if (gps.time.hour() < 10) Serial.print(F("0"));
    Serial.print(gps.time.hour());
    Serial.print(F(":"));
    if (gps.time.minute() < 10) Serial.print(F("0"));
    Serial.print(gps.time.minute());
    Serial.print(F(":"));
    if (gps.time.second() < 10) Serial.print(F("0"));
    Serial.print(gps.time.second());
    Serial.print(F("."));
    if (gps.time.centisecond() < 10) Serial.print(F("0"));
    Serial.print(gps.time.centisecond());
  }
  else
  {
    Serial.print(F("INVALID"));
  }
  Serial.println();
}

void UltrasonicSensor(int trigPin,int echoPin)
{
digitalWrite(trigPin, LOW);
delayMicroseconds(2);
digitalWrite(trigPin, HIGH);
delayMicroseconds(10);
digitalWrite(trigPin, LOW);
duration = pulseIn(echoPin, HIGH);
distance = (duration/2) / 29.1;
}
