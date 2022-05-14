#include "stepper.h"

Stepper::Stepper(int interface,int step_pin,int dir_pin): AccelStepper(interface,step_pin,dir_pin){
    profile = NO_ACCEL; //Default value.
}



void Stepper::setCurrentPosition(long position){
    AccelStepper::setCurrentPosition(position); 
    AccelStepper::setSpeed(cons_speed);
}

void Stepper::setSpeed(float speed){
    cons_speed = speed;
    AccelStepper::setSpeed(speed);
}

void Stepper::computeNewSpeed(){
    if(profile == NO_ACCEL){
        long distanceTo = distanceToGo();
        if (distanceTo == 0){
            AccelStepper::setCurrentPosition(currentPosition()); // Sets the speed to 0
        }else{
            setSpeed(cons_speed);
        }
    }else{
        AccelStepper::computeNewSpeed();
    }
}


void Stepper::setProfile(int new_profile){
    profile = new_profile;
}

boolean Stepper::run(){
    if (Stepper::runSpeed())
	    Stepper::computeNewSpeed();
    return speed() != 0.0 || distanceToGo() != 0;
}

void Stepper::moveTo(long absolute){
    AccelStepper::moveTo(absolute);
    if (profile == NO_ACCEL){
        Stepper::computeNewSpeed();

    }
}
