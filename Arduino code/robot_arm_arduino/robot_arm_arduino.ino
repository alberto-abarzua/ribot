#include <Servo.h>
#include <Vector.h> 
#include <Streaming.h>
#include <AccelStepper.h>
#include <MultiStepper.h>
// ------Constantes para recepcion de comandos por serial------
const byte numChars = 128;
char receivedChars[numChars]; 
boolean newData = false;
// ------Constantes para recepcion de comandos por serial------

//------Pin definitions-----

// Sensores
const int sensorPin1= A1; 
const int sensorPin2 = A2; 
const int sensorPin3 = A3; 
const int sensorPin4 = A4; 
const int sensorPin5 = A5; 
const int sensorPin6 = A6; 
const int sensorList[7] = {sensorPin1,sensorPin2,sensorPin2,sensorPin3,sensorPin4,sensorPin5,sensorPin6};

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
//Gripper servo
const int gripPin = 50;

//------Pin definitions-----

//------Variables y constantes------
const int amountOfSteppers = 7;
const int amountOfJoints = 6;
const double ratios[amountOfSteppers] = {20.0/200.0,20.0/155.0,20.0/155.0,(20.0/60.0)*(24.0/100.0),1.0,20.0/60.0,1.0}; //Guarda los ratios entre las poleas de cada motor
const int offsets[amountOfSteppers] = {121,39-55,39-55,-154+10,180,50,0}; // Guarda el la distancia entre el sensor de homing y el 0 real del brazo
const int isInverted[amountOfSteppers] = {false,false,false,true,false,true,true}; //verdadero o falso dependiendo si algun eje debe ser invertidos1 10
const int homedir[amountOfSteppers] = {1.0,-1.0,-1.0,-1.0,1.0,1.0,1.0};
const double speedmult[amountOfSteppers] = {1.0,1.0,1.0,0.6,1.0,1.0,1.0};
long positions[amountOfSteppers]; //lista que ocupa Multistepper para mover los 7 steppers

//------Variables y constantes------


//------- Inicio de los 7 motores y gripper
#define motorInterfaceType 1
AccelStepper motor1(motorInterfaceType, stepPin1, dirPin1);
AccelStepper motor2(motorInterfaceType, stepPin2, dirPin2);
AccelStepper motor3(motorInterfaceType, stepPin3, dirPin3);
AccelStepper motor4(motorInterfaceType, stepPin4, dirPin4);
AccelStepper motor5(motorInterfaceType, stepPin5, dirPin5);
AccelStepper motor6(motorInterfaceType, stepPin6, dirPin6);
AccelStepper motor7(motorInterfaceType, stepPin7, dirPin7);
AccelStepper listSteppers[7] = {
  motor1,
  motor2,
  motor3,
  motor4,
  motor5,
  motor6,
  motor7};
MultiStepper steppers; 
Servo gripper;
//------- Inicio de los 7 motores y gripper




//==========================================================
// ==================== SETUP ===================
//==========================================================
void setup() {
  Serial.begin(115200);
  gripper.attach(gripPin);
  // setup de los 7 steppers
  for (int i =0;i<7;i++){
    steppers.addStepper(listSteppers[i]);
    stepperSetup(listSteppers[i],i);
  }
  Serial.print("0\n"); // "0\n" <==> estoy listo para recibir info
}
//==========================================================
// ==================== SETUP ===================
//==========================================================









//==========================================================
// ==================== LOOP ===================
//==========================================================
void loop() {
  recvWithEndMarker();
  //tests();
  if (newData){
    if(receivedChars[0] == 'h'){ // if para realizar home de algun eje, ej: "h0\n" homea el eje 0
      int i = receivedChars[1] - 48; 
      homing(i,sensorList[i],listSteppers[i]);
      goOffset(i,listSteppers[i]);
    }else if (receivedChars[0] == 's'){ // if para mover los ejes entregando como input un angulo en grados, ej: "s1 90 s3 19\n" 
      int angle_list[7] = {0,0,0,0,0,0,0}; //mueve el eje 1 y 3 en 90 y 19 grados respectivamente.
      lineToList(receivedChars,angle_list);
        for (int j = 0;j<amountOfSteppers;j++){
            int pos = posRatio(angle_list[j]*1.0,j);
            if(j ==2){ // para evitar moviementos de mas solo podemos mover el primer eje con "s2" ya que este tiene dos motores.
              continue;
            }
            if(j==1){ // ajustamos la posicion de los dos motores del eje 1.
              positions[j] += pos;
              positions[j+1] += pos;
              continue;
            }
            positions[j] += pos; // caso para todos los otros ejes
        }
      }else if(receivedChars[0] == 't'){//<--------- if para mover los ejes entregando angulo en pasos (0-->1600) un revolucion ej: "t1 100 t5 500"
      int angle_list[7] = {0,0,0,0,0,0,0};
      lineToList(receivedChars,angle_list);
        for (int j = 0;j<amountOfSteppers;j++){
            int pos = ratio(angle_list[j]*1.0,j);
            if(j ==2){
              continue;
            }
            if(j==1){
              positions[j] += pos;
              positions[j+1] += pos;
              continue;
            }
            positions[j] += pos;
        }
      }else if (receivedChars[0] == 'i'){//<--------- if para entregar al serial las posiciones de todos los motores en steps ajustados a su ratio de polea.
        String res;
        for (int i =0; i<amountOfSteppers;i++){
          res +=String(ratiot(listSteppers[i].currentPosition(),i));
          res += ";";
        }
        res +="\n";
       Serial.print(res);
      }else if (receivedChars[0] == 'g'){ //<---------if para mover el servo gripper, recibe angulo entre 0-180 grados. ej: "g0 10" mueve el servo gripper en 10 grados.
        int gri[1] = {0};
        lineToList(receivedChars,gri);
        int current = gripper.read();
        int n = gri[0] + current;
        if (n>current){
          for (int i = current;i<n;i+=1){
            gripper.write(i);
            delay(30);
          }
        }else{
          for (int i = current; i>n;i-=1){
            gripper.write(i);
            delay(30);
          }
        }
      }else if (receivedChars[0] == 'r'){ //<---------if para entregar la posicion actual del servo gripper.
        Serial.print(String(gripper.read()) + "\n");
      }
 steppers.moveTo(positions); // Despues de recibir datos o info se debe llamar a que los motores se muevan a las posibles nuevas posiciones.
}
steppers.runSpeedToPosition(); // En caso de que los motores aun no esten en sus posiciones deseadas (positions), se llama esta funcion
// la cual pausa el loop hasta que todos los motores llegan a su destino.
showNewData(); // Funcion para poder nuevamente recibir info del serial, imprime "0\n" para indicar que el arduino esta disponible.
}
//==========================================================
// ==================== LOOP ===================
//==========================================================






//==========================================================
// ==================== MOTOR SETUP FUNC ===================
//==========================================================
void stepperSetup(AccelStepper &stepper,int i){
  stepper.setMaxSpeed(300);
  stepper.setAcceleration(20);
  int s = 40/ratios[i]*speedmult[i];
  stepper.setSpeed(s);
  stepper.setCurrentPosition(0);
  stepper.setPinsInverted(isInverted[i],false,false);
  
}
//==========================================================
// ==================== MOTOR SETUP FUNC ===================
//==========================================================





//==========================================================
// ====================HOMING FUNCTION =====================
//==========================================================

void goOffset(int num,AccelStepper &stepper){
  if (num == 1 || num == 2){
    listSteppers[1].setCurrentPosition(posRatio(offsets[num],num));
    listSteppers[2].setCurrentPosition(posRatio(offsets[num],num)); 
    positions[1] = 0;
    positions[2] = 0;
    steppers.moveTo(positions);
  }else{
    listSteppers[num].setCurrentPosition(posRatio(offsets[num],num));
    positions[num] = 0;
    steppers.moveTo(positions);
  }
}



void homing(int num,int sens,AccelStepper &stepper){
  if (num == 1 || num ==2){
    positions[1] = posRatio(360*homedir[num],1);
    positions[2] = posRatio(360*homedir[num],2);
    steppers.moveTo(positions);
    while(inRange(analogRead(sens))){
      steppers.run();
    }
    
  }else{
    int r = 360*homedir[num];
    positions[num] = posRatio(r,num);
    steppers.moveTo(positions);
    while(inRange(analogRead(sens))){
      steppers.run();
    }
  }
}
//==========================================================
// ====================HOMING FUNCTION =====================
//==========================================================





//==========================================================
// ==================== TEST FUNC ===================
//==========================================================
void tests(){
  for (int i =0;i<7;i++){
    Serial<<"M" + String(i) + ": ||"<< ratioPos(listSteppers[i].currentPosition(),i)<< "|| ";
    //Serial<<"S" + String(i) + ": ||"<< analogRead(sensorList[i])<< "|| ";
    
  }
  for (int i =0;i<7;i++){
    //Serial<<"M" + String(i) + ": ||"<< ratioPos(listSteppers[i].currentPosition(),i)<< "|| ";
    Serial<<"S" + String(i) + ": ||"<< analogRead(sensorList[i])<< "|| ";
    
  }
  Serial<<endl;
}

//==========================================================
// ==================== TEST FUNC ===================
//==========================================================





String arrayStr(bool arr[],int n){
  String result = " ";
  for (int i = 0; i<n;i++){
    result += "Motor " + String(i)+": "+ String(arr[i])+" ";
  }
  return result;
}

bool inRange(int a){
  return (a<560 && a>490);
}

double posRatio(int pos, int motorNumber){
  return (double((pos))/ratios[motorNumber])/1.8*8.0;
}

double ratioPos(int pos, int motorNumber){
  return (pos*ratios[motorNumber]/8*1.8);
}

double ratio(double pos,int motor){
  return (pos/ratios[motor]);
  
}

double ratiot(double pos,int motor){
  return (pos*ratios[motor]);
  
}













//==========================================================
//===============FUNCIONES DE COMUNICACION SERIAL ==========
//==========================================================

void lineToList(String v,int list[]){
        const int ELEMENT_COUNT = 32;
        int storage_array[ELEMENT_COUNT];
        Vector<int> num(storage_array);
        bool isNegative = false;
        num.clear()
;        v+=";";
        int currentMotor;
        for (int i =0;i<=v.length()+1;i++){
            if (v[i] == 's' || v[i] == 't' || v[i] == 'g'){
              //Serial<<v<<endl;
              //Serial.println(currentMotor);
              currentMotor = v[i+1]-'0';
              
              }
            if ((v[i] ==' ') || v[i] == ';'){
                int current = 0;
                for (int j = 0; j<num.size();j++){
                    current *= 10;
                    current +=(num[j]);  
                }
                num.clear();
                if (isNegative){
                    list[currentMotor] = -current;
                    isNegative = false;
                }else{
                    list[currentMotor] = current;
                }
            }else if((v[i]  != ' ')&&(v[i-2] !='s') &&(v[i-1]!='s') &&(v[i] !='s') &&(v[i-2] !='t') &&(v[i-1]!='t') &&(v[i] !='t') &&(v[i-2] !='g') &&(v[i-1]!='g') &&(v[i] !='g')){
                    if (v[i]==45){
                      isNegative = true;
                    }else{
                      num.push_back(v[i] - '0');
                    }
          
        }
        }

}


void recvWithEndMarker() {
 static byte ndx = 0;
 char endMarker = '\n';
 char rc;
 
 // if (Serial.available() > 0) {
           while (Serial.available() > 0 && newData == false) {
 rc = Serial.read();

 if (rc != endMarker) {
 receivedChars[ndx] = rc;
 ndx++;
 if (ndx >= numChars) {
 ndx = numChars - 1;
 }
 }
 else {
 receivedChars[ndx] = '\0'; // terminate the string
 ndx = 0;
 newData = true;
 }
 }
}

void showNewData() {
   if (newData == true) {
   Serial.print("0\n");
   newData = false;
   }
   
}

//==========================================================
//===============FUNCIONES DE COMUNICACION SERIAL ==========
//==========================================================
