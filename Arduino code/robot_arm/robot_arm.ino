#include <Servo.h>
#include <Streaming.h>
#include <AccelStepper.h>
#include <MultiStepper.h>

/*
 * Author: Alberto Abarzua
 */


//Serial comunication buffer
const int max_size = 512;
const int numSteppers = 7;

char buf[max_size];


/**
 * Variables used in loop.
 */
char op = ' ';
int n = 0;
long nums[numSteppers] = {0};
long result[numSteppers] = {0};
bool new_print = false;
bool testing = false;

//Motor parameters

const int micro_stepping = 8;
const int acc = 10000; // Accuracy of the angles received.
const double ratios[numSteppers] = {9.3,5.357,5.357,4.5*5.0,1.0,3.5,1.0};//Ratios between motor and joint (pulley)
const int inverted[numSteppers] = {true,false,false,false,false,true,false};

long positions[numSteppers] = {0};//Array to store the positions where the steppers should be. (in steps)
long angles[numSteppers] = {0}; // Array to store the angles of each joint (J1 J2 J2 J3 J4 J5 J6) // J2 is repeated because there are two steppers that controll it.

// Motor 1
const int stepPin1 = 52;
const int dirPin1 = 53;
// Motor 2
const int stepPin2 = 51;
const int dirPin2 = 50;
// Motor 3
const int stepPin3 =49;
const int dirPin3=48;
// Motor 4
const int stepPin4 = 47;
const int dirPin4 = 46;
// Motor 5
const int stepPin5 = 45;
const int dirPin5 = 44;
//Motor 6
const int stepPin6 = 43;
const int dirPin6 = 42;
//Motor 7
const int stepPin7 = 10;
const int dirPin7 = 11;

//Stepper motors

#define motorInterfaceType 1
AccelStepper motor1(motorInterfaceType, stepPin1, dirPin1);
AccelStepper motor2(motorInterfaceType, stepPin2, dirPin2);
AccelStepper motor3(motorInterfaceType, stepPin3, dirPin3);
AccelStepper motor4(motorInterfaceType, stepPin4, dirPin4);
AccelStepper motor5(motorInterfaceType, stepPin5, dirPin5);
AccelStepper motor6(motorInterfaceType, stepPin6, dirPin6);
AccelStepper motor7(motorInterfaceType, stepPin7, dirPin7);

AccelStepper *listSteppers[numSteppers] = {&motor1,&motor2,&motor3,&motor4,&motor5,&motor6,&motor7};

//Hall Sensors

// Joint 1
const int hall_1 = 7;
const int hall_2 = 6;
const int hall_3 = 5;
const int hall_4 = 4;
const int hall_5 = 3;
const int hall_6 = 2;


//Sensor list
const int num_sensors = 6;
const int sensor_list[] = {hall_1,hall_2,hall_3,hall_4,hall_5,hall_6};

MultiStepper steppers;

void setup() {
  Serial.begin(115200);
  for (int i =0;i<numSteppers;i++){
    steppers.addStepper((*listSteppers[i]));
    stepperSetup(i);
  }
  Serial.print("1\n");

  
}


void loop() {
  op = ' ';
  readLine(buf,nums,&op,&n);
  
  if (op == 'm'){ 
    /*
     * Move motors op:
     * 
     * Must follow this syntax: f"m{numSteppers} angle1 angle 2 ... angle_{numSteppers}"
     * example:
     *      m7 31415 31415 31415 31415 31415 31415 31415
     *      m7 7853 7853 7853 7853 7853 7853 7853
     *      m7 -7853 -7853 -7853 -7853 -7853 -7853 -7853
     *      m7 0 7853 7853 0 0 0 0
     *      m7 0 0 0 7853 0 0 0
     *      m7 7853 0 0 0 0 0 0
     *      m7 0 0 0 0 7853 0 0
     *      m7 0 0 0 0 0 7853 0
     *      m7 0 0 0 0 0 0 7853
     *      
     * IMPORTANT:
     *  The angles should be in radians*acc--> 3.1415*rad <--> 31415 [rad*acc]
     * 
     */
   
    new_print = true;
    //printArr(nums,numSteppers,"nums"); //<--Testing
    for (int i =0; i<numSteppers;i++){
      angles[i] += nums[i]; // Add to current angles the angles received in nums 
    }
    numsToRatios(result,angles); //
    //printArr(result,numSteppers,"result"); //<--Testing
    for (int i =0; i<numSteppers;i++){
      positions[i] = result[i]; // Add to current positions the new angles in steps
    }
    //printArr(positions,numSteppers,"positions"); //<--Testing
    //Serial.print("\n"); //<--Testing
    steppers.moveTo(positions); 
  }
  else if (op == 'i'){
    /**
     * Get current steps op:
     * 
     * Prints to the serial all the current position in steps of the motors.
     */
    for (int i =0;i<numSteppers;i++){
      long curPos = (*listSteppers[i]).currentPosition();
      Serial.print(curPos);
      if (i != numSteppers -1){
        Serial.print(" ");
      }
    }
    Serial.print("\n");
  }
  else if(op == 't'){ // Operation to turn on or off testing mode.
      testing = !testing;
    }
  

  if (testing){// This is testing mode, shows and reads all sensors.
    Serial.print("Sensors --> ");
    for (int i =0;i<num_sensors;i++){
      Serial.print("| S");
      Serial.print(i);
      Serial.print(" = ");
      Serial.print(digitalRead(sensor_list[i]) ? "off" : "on");
      Serial.print(" | ");
    }
      Serial.print("\n");
  }

    
  if (steppers.run() || new_print){
    long max_val= 0;
    for (int i =0;i <numSteppers;i++){
      long cur = listSteppers[i]->distanceToGo();
      if (abs(cur)>max_val){
        max_val = abs(cur);
      }
      //Serial.print(cur); //<--Testing
      //Serial.print(" "); //<--Testing
    }
    //Serial.print(" max_val: "); //<--Testing
    //Serial.print(max_val); //<--Testing
    if ((max_val <micro_stepping && new_print)){
      Serial.print("1\n");
      new_print = false;
    }
  }
}



/*
 * ------------------------- Beginning of stepper management functions -------------------------
 */
void stepperSetup(int i){
    double mult = 1.8;
    listSteppers[i]->setMaxSpeed(mult*5.0*ratios[i]*micro_stepping);
    listSteppers[i]->setPinsInverted(inverted[i],false,false);
    listSteppers[i]->setSpeed(mult*1.0*ratios[i]*micro_stepping);
    listSteppers[i]->setAcceleration(mult*2.0*ratios[i]*micro_stepping);
}

void numsToRatios(long *result,long *nums){
  //Gets a list of nums representing angles in radians*accuracy and converts them in steps for 
  // each of the robots joints.
  for (int i =0;i<numSteppers;i++){
    result[i] = (nums[i]*100*micro_stepping*ratios[i])/(PI*acc);
  }
}


/*
 * ------------------------- Ending of stepper management functions -------------------------
 */


// Used to print arrays during testing.
void printArr(long * arr,int n,char * label){
  Serial.print(label);
  Serial.print(" ");
  for (int i =0;i<n;i++){
    long value = arr[i];
    Serial.print(value);
    if (i != n-1){
      Serial.print(" ");
    }
    
  }
  Serial.println("");
}



/*
 * ------------------------- Beginning of Serial coms functions -------------------------
 */




// Recieves a string with n numbers separated by ' ' and stores then in the array nums.
void strToList(char * str, long * nums,int n){
  char* ini;
  char* fin;
  fin = str-1;
  int idx = 0;
  while (idx<n){
    fin+= 1;
    ini = fin;
    while(*fin != ' ' && *fin != '\0'){
      fin++;
    }
    char temp = *fin;
    *fin = '\0';
    nums[idx] = atol(ini);
    
    idx ++;
    *fin = temp;
  }
}


// Gets the operation that the program should do from the instruction represented by char * str.
void getOP(char * str,char *op,int * n){
  /* Operations should have this syntax:
     op = "m4 1 2 3 4"
     the operation of op is 'm'(operation should be a char) the number of inputs is 4 and they are (1,2,3,4).
  */
  *op = str[0];
  char *ptr = str;
  while (*ptr!= ' '){
    ptr++;
  }
  ptr++;
  char temp = *ptr;
  *ptr = '\0';
  *n = atoi(&str[1]);
  *ptr = temp;
 
}


//This function reads chars from Serial until a \n is read. Writes the string received on char * buf.
void readChars(char * buf,int max_size,bool* newData){
  bool reading = true;
  int static idx = 0;
  char read_char;
  while(Serial.available()> 0){
    *newData = true;
    read_char = Serial.read();
    
    if(read_char == '\n' || idx == max_size-1){
      buf[idx] = '\0';
      idx= 0;
      *newData = false;
      break;
    }else{
      buf[idx] = read_char;
      idx ++;
    }
  }
}

 // If there is data available in the serial buffer it will read.
 void readLine(char *buf,long * nums,char * op,int* n){
    bool newData;
    readChars(buf,max_size,&newData);//Reads the char from serial
    if (!newData){
      getOP(buf,op,n); // 
      strToList(&buf[3],nums,*n);
      
    }
    
 }


/*
 * ------------------------- Ending of Serial coms functions -------------------------
 */
