#ifndef stepper_h
#define stepper_h



#include "Arduino.h"

#include <AccelStepper.h>

#define NO_ACCEL 1 //Profile used for no acceleration
#define motorInterfaceType 1
#define ACCEL 2 // PROFILE USED FOR ACCELERATION.

class Stepper : public AccelStepper{
    private:
        int profile;
        long cons_speed;
    public :
        Stepper::Stepper(int interface,int step_pin,int dir_pin);
        void computeNewSpeed();
        void setProfile(int new_profile);
        void setCurrentPosition(long position);
        void setSpeed(float speed);
        boolean run();
        void moveTo(long absolute);
        


};

   
#endif
