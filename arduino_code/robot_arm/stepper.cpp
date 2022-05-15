#include "stepper.h"


/**
 * @brief author Alberto Abarzua
 * 
 * Simplified version of the library AccelStepper 
 * 
 *          https://github.com/waspinator/AccelStepper
 * 
 */


void Stepper::step(){
    //This part of the code is based from the library AccelStepper

    setOutputPins(direction ? 0b10 : 0b00); // Set direction first else get rogue pulses
    setOutputPins(direction ? 0b11 : 0b01); // step HIGH
    // Caution 200ns setup time 
    // Delay the minimum allowed pulse width
    delayMicroseconds(minPulseWidth);
    setOutputPins(direction ? 0b10 : 0b00); // step LOW
}


void Stepper::setOutputPins(uint8_t mask){
    for (uint8_t i = 0; i < 2; i++)
	digitalWrite(pins[i], (mask & (1 << i)) ? (HIGH ^ pin_inverted[i]) : (LOW ^ pin_inverted[i]));
}

void Stepper::invertDirPin(bool inverted){
    pin_inverted[1] = inverted;
}

Stepper::Stepper(int step_pin,int dir_pin){
    pins[0] = step_pin;
    pins[1] = dir_pin;
    pinMode(pins[0], OUTPUT);
    pinMode(pins[1], OUTPUT);
}

void Stepper::setSpeed(float new_speed){
    set_speed = new_speed;
}

void Stepper::setCurSpeed(float new_speed){
    if(new_speed == cur_speed){
        return;
    }

    if (new_speed == 0.0){ 
	    step_interval = 0;
    }
    cur_speed = new_speed;
    step_interval = fabs(1000000.0 / cur_speed);
}

void Stepper::computeSpeed(){
    if (distanceToGo() == 0){
        setCurSpeed(0.0);

    }else{
        setCurSpeed(set_speed);

    }
    updateDir();
}


bool Stepper::run(){
    if(takeSteps()){
        computeSpeed();
        return true;
    }
    return false;
}
long Stepper::distanceToGo(){
    return desired_pos-cur_pos;
}
bool Stepper::takeSteps(){
    // Dont do anything unless we actually have a step interval
    if (!step_interval)
	    return false;

    unsigned long time = micros();   
    if (time - last_step_time >= step_interval){
        if (direction == DIRECTION_CW){   
            cur_pos += 1;// Clockwise
        }
        else{
            cur_pos -= 1;// Anticlockwise  
        }
        step();
        last_step_time = time; // Caution: does not account for costs in step()
        return true;
    }
    return false;
}

void Stepper::moveTo(long new_target){
        if(new_target != desired_pos){
            desired_pos = new_target;
            computeSpeed();
            
        }
}   

void Stepper::updateDir(){
    if(cur_pos>desired_pos){
        direction = DIRECTION_CCW;
    }else{
        direction = DIRECTION_CW;
    }
}

void Stepper::setCurrentPosition(long new_pos){
    cur_pos = new_pos;
    desired_pos  = new_pos;
    computeSpeed();

}
long Stepper::getCurrentPosition(){
    return cur_pos;
}

long Stepper::getCurSpeed(){
    return cur_speed;
}
long Stepper::getTarget(){
    return desired_pos;
}