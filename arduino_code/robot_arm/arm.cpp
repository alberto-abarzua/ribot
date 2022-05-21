#include "Arduino.h"
#include "arm.h"



/**
 * @brief author Alberto Abarzua
 * 
 */

/**
-----------------------------
-----------     Sensor     -----------
-----------------------------

 */


 Sensor::Sensor(int new_pin){
     pin = new_pin;
 }


bool Sensor::read(){
    return !digitalRead(pin);
}


/**
-----------------------------
-----------     Joint     -----------
-----------------------------

 */



Joint::Joint(double a_ratio,bool a_inverted,int a_homing_dir,int a_offset,int joint_num_steppers){
    jn_steppers = joint_num_steppers;

    motors =(Stepper **) malloc(sizeof (Stepper *)*joint_num_steppers);
    sensor = (Sensor *) malloc(sizeof(Sensor *));
    for (int i =0;i<jn_steppers;i++) motors[i]=NULL;
    ratio = a_ratio;
    inverted = a_inverted;
    homing_dir = a_homing_dir;
    offset = a_offset;
    angle =0;
    position =0;
}
Joint::Joint(double a_ratio,bool a_inverted,int a_homing_dir,int a_offset,int joint_num_steppers,double a_speed_multiplier){
    jn_steppers = joint_num_steppers;

    motors =(Stepper **) malloc(sizeof (Stepper *)*joint_num_steppers);
    sensor = (Sensor *) malloc(sizeof(Sensor *));
    for (int i =0;i<jn_steppers;i++) motors[i]=NULL;
    ratio = a_ratio;
    inverted = a_inverted;
    homing_dir = a_homing_dir;
    offset = a_offset;
    angle =0;
    position =0;
    speed_multiplier = a_speed_multiplier;
}


void Joint::home(){
    int times_activated = 0;
    int tolerance = 7;
    while(true){
        if (sensor->read()){
            times_activated++;
        }else{
            times_activated =0;
        }

        if (times_activated>=tolerance){
            for (int i =0 ;i<jn_steppers;i++){
                motors[i]->setCurrentPosition(offset*homing_dir*-1);
                position=0;
                angle=0;
                motors[i]->moveTo(position);
            }
                break;
        }
        for(int i =0;i<jn_steppers;i++){
            if(motors[i]->distanceToGo() == 0){ // Homing failed, we return to avoid soft lock.
                return;
            }
            motors[i]->run();
        }
    }
}


void Joint::create_motor(int step_pin,int dir_pin){
    int idx = 0;
    while(motors[idx]!=NULL) idx++;
    motors[idx] = new Stepper(step_pin, dir_pin);
    
 }

 void Joint::motor_setup(){
     double m_speed = speed_multiplier*SPEED_CONSTANT*ratio*MICRO_STEPPING;
     for (int i=0;i<jn_steppers;i++){
         motors[i]->invertDirPin(inverted);
         motors[i]->setCurrentPosition(0);
         motors[i]->setSpeed(m_speed);
         
     }

 }
void Joint::create_sensor(int pin){
    sensor = new Sensor(pin);
 }

void Joint::show(){
    Serial.print("Joint ");
    Serial.print(index);
    Serial.print(" Motor speed ");
    Serial.print(motors[0]->getCurSpeed());
    Serial.print(" Joint ratio: ");
    Serial.print(ratio);
    Serial.println("");

}

void Joint::add_angle(long val){
    angle+=val;
    position = (long) ((ratio*angle*100*MICRO_STEPPING)/(PI*ACC));
    for(int i =0;i<jn_steppers;i++){
        motors[i]->moveTo(position);
    }
}

void Joint::launch_home(){
    add_angle(1.3*3.1415*ACC*homing_dir);
    for (int i =0 ;i<jn_steppers;i++){
      motors[i]->moveTo(position);
    }
}

void Joint::set_offset(long new_offset){
    offset = new_offset;
}
void Joint::show_offset(){
    Serial.print("Joint ");
    Serial.print(index);
    Serial.print(" current offset: ");
    Serial.print(offset);
}

/**
-----------------------------
-----------     Arm     -----------
-----------------------------

 */


Arm::Arm(int n_joints){
    num_joins = n_joints;
    joints = (Joint **)malloc(sizeof(Joint *)*n_joints);
    sensors =(Sensor **) malloc(sizeof(Sensor *)*n_joints);
    l_positions = (long *) malloc(sizeof(long)*n_joints);
    for(int i =0;i<num_joins;i++)  l_positions[i]=0;
    idx=0;
    m_idx =0;
    num_motors =0;

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



bool Arm::left_to_go(){
    for (int i =0;i<num_joins;i++){
        int tolerance = 10*joints[i]->ratio;
        if(abs(motors[i]->distanceToGo()) >= tolerance){
            return true;
        }
    }
    return false;
}

void Arm::create_gripper(int pin){
    gripper = new Servo();
    gripper->attach(pin);
    gripper->write(100);
}

void Arm::set_gripper_angle(int val){
    gripper->write(val);
}



void Arm::run(){
    for (int i =0;i<num_motors;i++){
        motors[i]->run();
    }
}
void Arm::add(long * args){
    for(int i =0;i<num_joins;i++){
        joints[i]->add_angle(args[i]);
        l_positions[i] = (joints[i]->position);

    }

}
void Arm::show_pos(){
    Serial.print("Arms LPositions: ");
    Serial.print(" ");
    for (int i =0;i<num_joins;i++){
        Serial.print(l_positions[i]);
        Serial.print(" ");

    }
    Serial.print("Arms angles: ");
    Serial.print(" ");
    for (int i =0;i<num_joins;i++){
        Serial.print(joints[i]->angle);
        Serial.print(" ");

    }
    Serial.print("Motors Positions: ");
    Serial.print(" ");
    for (int i =0;i<num_joins;i++){
        Serial.print(motors[i]->getCurrentPosition());
        Serial.print(" ");

    }
    Serial.print("TargetPosition: ");
    Serial.print(" ");
    for (int i =0;i<num_joins;i++){
        Serial.print(motors[i]->getTarget());
        Serial.print(" ");

    }

    Serial.print("Left To Go?");
    Serial.print(" ");
    Serial.print(left_to_go()? " MOVING ": " STOPPED ");

    Serial.print("Distance to go: ");
    Serial.print(" ");
    for (int i =0;i<num_joins;i++){
        Serial.print(motors[i]->distanceToGo());
        Serial.print(" ");

    }
    
}



void Arm::home(){
    for(int i =0;i< num_joins;i++){
        joints[i]->launch_home();
    }
    for(int i =0;i< num_joins;i++){
        joints[i]->home();
    }
}

void Arm::home_joint(int join_idx){
        joints[join_idx]->launch_home();
        joints[join_idx]->home();
}

void Arm::show_sensors(){
    Serial.print("Sensors: ");
    for (int i =0;i<num_joins;i++){
        Serial.print(" ");
        Serial.print("S");
        Serial.print(i+1);
        Serial.print(" ");
        Serial.print(joints[i]->sensor->read()?"ACTIVE" : "OFF");
    }
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
    motors =(Stepper **) malloc(sizeof(Stepper *)*num_motors);
    int spot= 0;
    for (int i =0;i<num_joins;i++){

        joints[i]->motor_setup();
        for (int j =0;j<joints[i]->jn_steppers;j++){
            motors[spot] = joints[i]->motors[j];
            //steppers->addStepper(*motors[spot]);
            spot ++;
        }
    }

}


void Arm::show_offsets(){
    for(int i =0;i<num_joins;i++){
        joints[i]->show_offset();
        Serial.print("\n");
    }
}

void Arm::show_gripper(){
    Serial.print("Gripper servo is at: ");
    Serial.println(gripper->read());   
}
