#include <Servo.h>
#include <Streaming.h>
#include <AccelStepper.h>
#include <MultiStepper.h>

/*
 * Author: Alberto Abarzua
 */


//Serial comunication buffer
const int max_size = 100;

char buf[max_size];

//Motor parameters
const int numSteppers = 1;
const int micro_stepping = 32;
const int acc = 1000;
const double ratios[numSteppers] = {1.0};//Ratios between motor and joint (pulley)

long positions[numSteppers] = {0};

//Motor1
const int stepPin1 = 22;
const int dirPin1 = 24;

void readLine(char *buf,long * nums,char * op,int* n);

//Stepper motors

#define motorInterfaceType 1
AccelStepper motor1(motorInterfaceType, stepPin1, dirPin1);
AccelStepper *listSteppers[numSteppers] = {&motor1};

MultiStepper steppers;

void setup() {
  Serial.begin(9600);
  for (int i =0;i<numSteppers;i++){
    steppers.addStepper((*listSteppers[i]));
    stepperSetup(i);
  }
}


void loop() {
  
  char op = ' ';
  int n = 0;
  long nums[numSteppers] = {0};
  readLine(buf,nums,&op,&n);
  if (op == 'm'){ // Move motors op
    long result[numSteppers];
    numsToRatios(result,nums);
    for (int i =0; i<numSteppers;i++){
      positions[i] += result[i];
    }
    steppers.moveTo(positions); 
  }
  if (op == 'i'){
    for (int i =0;i<numSteppers;i++){
      long curPos = (*listSteppers[i]).currentPosition();
      Serial.print(curPos);
      Serial.print(" ");
     
    }
    Serial.print("\n");
  }
  
  steppers.run();
}



/*
 * ------------------------- Beginning of stepper management functions -------------------------
 */
void stepperSetup(int i){
    listSteppers[i]->setMaxSpeed(300.0*ratios[i]);
    listSteppers[i]->setAcceleration(100.0*ratios[i]);
    Serial.println(&(*listSteppers[i])==&motor1);
}

void numsToRatios(long result[],long nums[]){
  //Gets a list of nums representing angles in radians*accuracy and converts them in steps for 
  // each of the robots joints.
  for (int i =0;i<numSteppers;i++){
    result[i] = (nums[i]*100*micro_stepping)/(PI*acc);
  }
}


/*
 * ------------------------- Ending of stepper management functions -------------------------
 */







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
