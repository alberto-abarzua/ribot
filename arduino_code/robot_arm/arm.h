#ifndef arm_h
#define arm_h

#include "Arduino.h"
#include "stepper.h"
#include <Servo.h>

/**
 * @brief author Alberto Abarzua
 * 
 */

#define MICRO_STEPPING 16
#define ACC 10000
#define SPEED_CONSTANT 15.0// Speed base mutliplier for all joints.
#define motorInterfaceType 1

/**
 * @brief Sensor class, used to create a sensor that each joint uses
 * 
 */
class Sensor{
  private:
    int pin;
  public:
    Sensor(int new_pin);
    /**
     * @brief Gets the status of the sensor
     * 
     * @return true if it is activated
     * @return false if it is not activated
     */
    bool read();
};


/**
 * @brief Joint class, used to create  the joints of the robot.
 * 
 */
class Joint{
  public:
    int index;
    double ratio;
    bool inverted;
    int homing_dir;
    int offset;
    long angle;
    long position;
    int jn_steppers;
    Sensor * sensor;
    long motor_speed;
    Stepper ** motors;
    double speed_multiplier =1.0;
    Joint::Joint(double a_ratio,bool a_inverted,int a_homing_dir,int a_offset,int joint_num_steppers);
    Joint::Joint(double a_ratio,bool a_inverted,int a_homing_dir,int a_offset,int joint_num_steppers,double a_speed_multiplier);
    /**
     * @brief Creates a new accelstepper motor for the joint.
     * 
     * @param step_pin step pin of the new motor
     * @param dir_pin direction pin of the new motor
     */
    void Joint::create_motor(int step_pin,int dir_pin);
    /**
     * @brief Creates a new sensor for the joint
     * 
     * @param pin 
     */
    void Joint::create_sensor(int pin);
    /**
     * @brief Prints to serial a string representation of the joint
     * 
     */
    void Joint::show();
    /**
     * @brief Runs the comands to setup the motors of the joint.
     * 
     */
    void Joint::motor_setup();
    /**
     * @brief Adds an angle to the angle variable, and updates it's position in steps.
     * 
     * @param val 
     */
    void Joint::add_angle(long val);
    /**
     * @brief Statrs the homing proces for the joint.
     * 
     */
    void Joint::launch_home();
    /**
     * @brief Runs the homing procedure of the joint.
     * 
     * @param m Multistepper used to run the other steppers.
     */
    void Joint::home();
    /**
     * @brief Sets a new offset for the joint
     * 
     * @param new_offset new value for offset
     */
    void Joint::set_offset(long new_offset);
    /**
     * @brief prints the offset of the joint.
     * 
     */
    void Joint::show_offset();

};



/**
 * @brief Arm class, used to create a new robot arm.
 * 
 */
class Arm{
  public:
  
    int num_joins;
    int idx;
    int  m_idx;
    long * l_positions;

    Joint ** joints;
    Stepper ** motors;
    Sensor ** sensors;
    int num_motors;
    Servo * gripper;

    Arm::Arm(int n_joints);

    /**
     * @brief Registers a joint to the arm
     * 
     * @param joint joint to be added
     */
    void Arm::register_joint(Joint* joint);
    /**
     * @brief Gets the motors of each joint and stores them in the motors variable, it 
     * runs motor_setup for all the joints and creates register the motor to Multistepper steppers.
     * 
     */
    void Arm::build_joints();

    /**
     * @brief Prints to serial a string representation of the arm.
     * 
     */
    void Arm::show();
    /**
     * @brief Creates a new servo registered to the arm. 
     * 
     * @param pin 
     */
    void Arm::create_gripper(int pin);
    /**
     * @brief Makes the arm and it's motors move to the desired positions.
     * 
     */
    void Arm::run();
    /**
     * @brief Adds angles to each joint of the arm. (runs add_angle() for each joint with its respective value in args.)
     * 
     * @param args array with angles for each joint.
     */
    void Arm::add(long * args);
    /**
     * @brief Prints to serial the current angles and positions of each joint.
     * 
     */
    void Arm::show_pos();
    /**
     * @brief Homes all the joints of the arm.
     * 
     */
    void Arm::home();
    /**
     * @brief Prints to serial the reading of each sensor of each joint of the arm.
     * 
     */
    void show_sensors();
    /**
     * @brief Sets the angle of the grippers servo.
     * 
     */
    void Arm::set_gripper_angle(int val);
    /**
     * @brief Checks if the motors have a distance to go.
     * 
     * @return true if the motors are still runing (distance to go)
     * @return false if the motors have reached their desired positions.
     */
    bool Arm::left_to_go();
    /**
     * @brief Starts and runs the homing procedure for a certain joint (determined by their index.)
     * 
     * @param join_idx joint index of the joint that will be homed.
     */
    void Arm::home_joint(int join_idx);
    /**
     * @brief Shows the offsets of each joint of the arm (prints to serial.)
     * 
     */
    void Arm::show_offsets();
    /**
     * @brief Prints to serial the current angle of the gripper.
     * 
     */
    void Arm::show_gripper();
    
};


#endif