#ifndef stepper_h
#define stepper_h
#include "Arduino.h"

/**
 * @brief author Alberto Abarzua
 * 
 * Simplified version of the library AccelStepper 
 * 
 *          https://github.com/waspinator/AccelStepper
 * 
 */

typedef enum
    {
	      DIRECTION_CCW = 0,  ///< Counter-Clockwise
        DIRECTION_CW  = 1   ///< Clockwise
    } Direction;

class Stepper {
  private:
    //Variables
    long cur_pos =0; // Current position of the motor
    long desired_pos=0; // Target position to run to.
    int dir_pin; // Dir pin of driver
    int step_pin; //Step pin of driver
    int pins[2]; // Array to store the pins
    int pin_inverted[2] = {0}; //Array to store if each pin is inverted or not.
    long cur_speed=0; //Current speed of the motor
    long set_speed=0; //Speed the motor will move if cur_pos != desired_pos
    bool direction; // Direction the motor has to step
    unsigned long  last_step_time; //Last step time (in microseconds)
    unsigned long  step_interval= 0; // interval between steps (in microseconds)

    unsigned int   minPulseWidth =1; /// The minimum allowed pulse width in microseconds
    /**
     * @brief Makes the stepper motor take a step.
     * 
     */
    void Stepper::step();
    /**
     * @brief Sets the pins (step and dir) High or Low. The pins statuses are stored in mask
     * 
     * bit 0 of the mask corresponds to _pin[0]
     * bit 1 of the mask corresponds to _pin[1]
     * 
     * @param mask mask containing the pin info.
     */
    void Stepper::setOutputPins(uint8_t mask);
    /**
     * @brief Computes the new speed that the motors should have,
     * 
     *      sets speeed and step interval to 0 if desired_pos == cur_pos
     * 
     *      sets speeed and step interval to set_speed if desired_pos == cur_pos
     *      
     * 
     */
    void Stepper::computeSpeed();
    /**
     * @brief If a step is due, the current positino is updated and a step is taken.
     * 
     * @return true if a step was taken
     * @return false if no steps where due/taken
     */
    bool Stepper::takeSteps();
    /**
     * @brief Sets the current speed of the motor
     * 
     * @param new_speed new speed to be set.
     */
    void Stepper::setCurSpeed(float new_speed);
    /**
     * @brief Updates the directcion the stepers should spin
     * 
     */
    void Stepper::updateDir();
  public:
  /**
   * @brief Construct a new Stepper:: Stepper object
   * 
   * @param step_pin Step pin connected to stepper driver
   * @param dir_pin Dir pin connected to stepper driver
   */
    Stepper::Stepper(int step_pin,int dir_pin);
    /**
     * @brief Inverts the direction of the stepper motor. (Inverts dirpin outpus)
     * 
     * @param inverted true if the direction should be inverted.
     */
    void Stepper::invertDirPin(bool inverted);
    /**
     * @brief Sets the param set_speed to speed,
     * 
     * @param speed new value for set_speed
     */
    void Stepper::setSpeed(float speed);
    /**
     * @brief Calls takeStep and computeSpeed to make the stepper run. Should be called as aften as possible
     * 
     * @return true 
     * @return false 
     */
    bool Stepper::run();
    /**
     * @brief Gets the difference between the current position and the target position.
     * 
     * @return long distance the stepper has to travel until reaching desired pos.
     */
    long Stepper::distanceToGo();
    /**
     * @brief Updates the desired_pos of the stepper, and calls computeSpeed()
     * 
     * @param new_target 
     */
    void Stepper::moveTo(long new_target);
    /**
     * @brief Sets the current position and desired position.
     * 
     * @param new_pos New vale for current and desired positions.
     */
    void Stepper::setCurrentPosition(long new_pos);
    /**
     * @brief Gets the current position of the motor
     * 
     * @return long current position of the motor
     */
    long Stepper::getCurrentPosition();
    /**
     * @brief Gets the current speed of the motor, this is 0 or set_speed.
     * 
     * @return long current position of the motor.
     */
    long Stepper::getCurSpeed();

    /**
     * @brief Gets the set_speed of this stepper
     * 
     * @return long set_speed parameter
     */
    long Stepper::getSetSpeed();

    /**
     * @brief Gets the target position of the motor. (desired_pos)
     * 
     * @return long returns desired_pos
     */
    long Stepper::getTarget();



    

};
   
#endif
