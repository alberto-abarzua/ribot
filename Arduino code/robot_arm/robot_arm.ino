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

const int micro_stepping = 16;
const int acc = 10000; // Accuracy of the angles received.
const double ratios[numSteppers] = {9.3,5.357,5.357,4.5*5.0,1.0,3.5,1.0};//Ratios between motor and joint (pulley)
const int inverted[numSteppers] = {true,false,false,false,false,true,false};
const int homing_dir[6] = {1,1,1,1,-1,-1};
const int offsets[] = {-3234*(micro_stepping/8),-1250*(micro_stepping/8),(-5186+8998)*(micro_stepping/8),-435*(micro_stepping/8),-566*(micro_stepping/8),0}; // Offsets of each joint in steps

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

// Servo motor for gripper

Servo gripper;

const int gripper_pin = 8;



void setup() {
  Serial.begin(115200);
  for (int i =0;i<numSteppers;i++){
    steppers.addStepper((*listSteppers[i]));
    stepperSetup(i);
  }
  gripper.attach(gripper_pin);
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
     *      m7 7853 0 0 0 0 0 0
     *      m7 0 7853 7853 0 0 0 0
     *      m7 0 0 0 7853 0 0 0
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
  else if (op == 'g'){// Operation to move the gripper servo motor RELATIVE 
    /**
     * Commands should follow this syntax:
     * 
     * g1 degress --> "g1 20" moves the servo motor 20 degrees from its current position
     */
    new_print = true;
    if (n == 1){
      int newVal = nums[0] + gripper.read();
      if (newVal>170){
        newVal = 170;
      }
      if (newVal<80){
        newVal = 80;
      }
      gripper.write(newVal);
      delay(15);
    }else if(n==2){ // Shows the current angle of the gripper servo.
      Serial.println(gripper.read());
    }else if (n ==3){ // Operation to move the gripper servo motor ABSOLUTE
    /**
     * Commands should follow this syntax:
     * 
     * g1 degress --> "g1 20" moves the servo motor 20 degrees from its current position
     */
     int newVal = nums[0];
      if (newVal>170){
        newVal = 170;
      }
      if (newVal<80){
        newVal = 80;
      }
      gripper.write(newVal);
      delay(15);
      
    }
  }else if (op == 'h'){ // Homing operation
    new_print = true;
    if (n ==10){
      for(int i =0;i<6;i++){
        homeJoint(i);
      }
    }else{
      homeJoint(n);
      
    }
  }
  
  

  if (testing){// This is testing mode, shows and reads all sensors.
    Serial.print("Sensors --> ");
    for (int i =0;i<num_sensors;i++){
      Serial.print("| S");
      Serial.print(i);
      Serial.print(" = ");
      Serial.print(digitalRead(sensor_list[i])? "off" :"on");
      Serial.print(" | ");
    }
      Serial.print("\n");
  }

    
  if (steppers.run() || new_print){
    long max_val= 0;
    for (int i =0;i <numSteppers;i++){
      long cur = abs(listSteppers[i]->distanceToGo());
      if (cur>max_val){
        max_val = cur;
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
    double mult = 3.2;
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
void stepsToAngles(long *result,long *nums){
  //Gets a list of nums representing steps and converts them into radians*accuracy
  for (int i =0;i<numSteppers;i++){

    result[i] = (PI*acc)/(nums[i]*100*micro_stepping*ratios[i]);
  }
}

void homeJoint(int i){
  int c =0;
  if (i== 1){ // Homing joint 1 ( two motors)
      angles[i] += 3.1415*acc*homing_dir[i]; 
      angles[i+1] += 3.1415*acc*homing_dir[i];
      numsToRatios(result,angles);
      positions[i] = result[i];
      positions[i+1] = result[i+1];
      steppers.moveTo(positions);
      
      while(true){
        if (digitalRead(sensor_list[i]) == 0){
          c++;
        }else{
          c=0;
        }
        
        if (c>=7){
         
          listSteppers[i]->setCurrentPosition(offsets[i]*homing_dir[i]*-1);
          listSteppers[i+1]->setCurrentPosition(offsets[i]*homing_dir[i]*-1);
          positions[i] = 0;
          positions[i+1] = 0;
          angles[i] = 0;
          angles[i+1] = 0;
          steppers.moveTo(positions);
          break;
        }
        steppers.run();
    }
  }else{
    int prev = i;
    if (i >0){
      i ++;
    }
    angles[i] += 2*3.1415*acc*homing_dir[prev]; 
    numsToRatios(result,angles);
    positions[i] = result[i];
    steppers.moveTo(positions);
    while(true){
      if (digitalRead(sensor_list[prev]) == 0){
          c++;
        }else{
          c=0;
        }
      
      if (c>=7){
        listSteppers[i]->setCurrentPosition(offsets[prev]*homing_dir[prev]*-1);
        positions[i] = 0;
        angles[i] =0;
        steppers.moveTo(positions);
        break;
      }
      steppers.run();
  }
    
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
