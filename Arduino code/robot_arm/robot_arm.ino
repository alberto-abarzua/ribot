#include <Servo.h>
#include <Streaming.h>
#include <AccelStepper.h>
#include <MultiStepper.h>

/*
 * Author: Alberto Abarzua
 */


//Serial comunication buffer
const int max_size = 100;
const int numSteppers = 7;

char buf[max_size];

char op = ' ';
int n = 0;

long nums[numSteppers] = {0};

long result[numSteppers] = {0};

//Motor parameters

const int micro_stepping = 32;
const int acc = 10000;
const double ratios[numSteppers] = {1.0,1.0,1.0,1.0,1.0,1.0,1.0};//Ratios between motor and joint (pulley)

long positions[numSteppers] = {0};

// Motor 1
const int stepPin1 = 22;
const int dirPin1 = 24;
// Motor 2
const int stepPin2 = 42;
const int dirPin2 = 44;
// Motor 3
const int stepPin3 =46;
const int dirPin3=48;
// Motor 4
const int stepPin4 = 38;
const int dirPin4 = 40;
// Motor 5
const int stepPin5 = 34;
const int dirPin5 = 36;
//Motor 6
const int stepPin6 = 30;
const int dirPin6 = 32;
//Motor 7
const int stepPin7 = 26;
const int dirPin7 = 28;

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

MultiStepper steppers;

void setup() {
  Serial.begin(115200);
  for (int i =0;i<numSteppers;i++){
    steppers.addStepper((*listSteppers[i]));
    stepperSetup(i);
  }
  Serial.println("1");

  
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
     *      
     * IMPORTANT:
     *  The angles should be in radians*acc--> 3.1415*rad <--> 31415 [rad*acc]
     * 
     */
    numsToRatios(result,nums);
    delay(1);
    //printArr(result,numSteppers,"result");
    //printArr(nums,numSteppers,"nums");
    for (int i =0; i<numSteppers;i++){
      positions[i] += result[i];
    }
    //printArr(positions,numSteppers,"positions");
    Serial.println("");
    steppers.moveTo(positions); 
  }
  if (op == 'i'){
    /**
     * Get current steps op:
     * 
     * Prints to the serial all the current position in steps of the motors.
     */
    for (int i =0;i<numSteppers;i++){
      long curPos = (*listSteppers[i]).currentPosition();
      Serial.print(positions[i]);
      if (i != numSteppers -1){
        Serial.print(" ");
      }
    }
    Serial.print("\n");
  }
  Serial.println("1");
  steppers.run();
}



/*
 * ------------------------- Beginning of stepper management functions -------------------------
 */
void stepperSetup(int i){
    listSteppers[i]->setMaxSpeed(300.0*ratios[i]);
    listSteppers[i]->setAcceleration(100.0*ratios[i]);
}

void numsToRatios(long *result,long *nums){
  //Gets a list of nums representing angles in radians*accuracy and converts them in steps for 
  // each of the robots joints.
  for (int i =0;i<numSteppers;i++){
    result[i] = (nums[i]*100*micro_stepping)/(PI*acc);
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
    nums[idx] = atoi(ini);
    
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
