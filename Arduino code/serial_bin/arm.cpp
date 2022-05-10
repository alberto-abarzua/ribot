#include "Arduino.h"
#include "arm.h"


#define motorInterfaceType 1
const int MICRO_STEPPING = 8;
const int ACC= 10000; // Accuracy of the angles received.
 Sensor::Sensor(int new_pin){
     pin = new_pin;
 }


Joint::Joint(double a_ratio,bool a_inverted,int a_homing_dir,int joint_num_steppers){
    jn_steppers = joint_num_steppers;

    motors =(AccelStepper **) malloc(sizeof (AccelStepper *)*joint_num_steppers);
    sensor = (Sensor *) malloc(sizeof(Sensor *));
    for (int i =0;i<jn_steppers;i++) motors[i]=NULL;
    ratio = a_ratio;
    inverted = a_inverted;
    homing_dir = a_homing_dir;
    offset = 0;
    angle =0;
    position =0;
}


void Joint::create_motor(int step_pin,int dir_pin){
    int idx = 0;
    while(motors[idx]!=NULL) idx++;
    motors[idx] = new AccelStepper(motorInterfaceType, step_pin, dir_pin);
    
 }

 void Joint::motor_setup(){
     double mult = (5.0/8.0)*6.0;
     for (int i=0;i<jn_steppers;i++){
         motors[i]->setPinsInverted(inverted,false,false);
         motors[i]->setMaxSpeed(mult*2.0*ratio*MICRO_STEPPING);
         motors[i]->setSpeed(mult*ratio*MICRO_STEPPING);
         motors[i]->setAcceleration(mult*30.0*ratio*MICRO_STEPPING);
         
     }

 }
void Joint::create_sensor(int pin){
    sensor = new Sensor(pin);
 }

void Joint::show(){
    Serial.print("Joint ");
    Serial.print(index);
    Serial.print("  nmotors: ");
    Serial.println(jn_steppers);
}

Arm::Arm(int n_joints){
    num_joins = n_joints;
    joints = (Joint **)malloc(sizeof(Joint *)*n_joints);
    sensors =(Sensor **) malloc(sizeof(Sensor *)*n_joints);
    idx=0;
    m_idx =0;
    num_motors =0;


}
void Arm::register_joint(Joint* joint){
    joints[idx] = joint;
    joints[idx]->index = idx;
    idx++;
}
void Arm::build_joints(){
    for (int i =0;i<num_joins;i++){
        num_motors+= joints[i]->jn_steppers; //First count the amount of motors
    }
    //We create an array to store them
    motors =(AccelStepper **) malloc(sizeof(AccelStepper *)*num_motors);
    int spot= 0;
    for (int i =0;i<num_joins;i++){

        joints[i]->motor_setup();
        for (int j =0;j<joints[i]->jn_steppers;j++){
            motors[spot] = joints[i]->motors[j];
            steppers.addStepper(*motors[spot]);
            spot ++;
        }
    }

}

void Arm::show(){
    Serial.print("Num motors ");
    Serial.print(num_motors);
    Serial.println("  -  ");
    for(int i =0;i<num_joins;i++){
        joints[i]->show();
    }
    Serial.println("");

}

void Arm::create_gripper(int pin){
    gripper.attach(pin);
}

void Joint::add_angle(long val){
    angle+=val;
    position = (long) ((angle*100*MICRO_STEPPING*ratio)/(PI*ACC));
}

void Arm::run(){
    steppers.moveTo(l_positions);
}
void Arm::add(long * args){
    for(int i =0;i<num_joins;i++){
        joints[i]->add_angle(args[i]);
        l_positions[i] = (joints[i]->position);

    }
}
void Arm::show_pos(){
    Serial.print("Arms Positions: ");
    Serial.print(" ");
    for (int i =0;i<num_joins;i++){
        Serial.print(joints[i]->position);
        Serial.print(" ");

    }
    Serial.print("Arms angles: ");
    Serial.print(" ");
    for (int i =0;i<num_joins;i++){
        Serial.print(joints[i]->angle);
        Serial.print(" ");

    }




}

