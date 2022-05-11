#ifndef arm_h
#define arm_h
#include <AccelStepper.h>
#include <MultiStepper.h>
#include <Servo.h>



#define MICRO_STEPPING 16
#define ACC 10000
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
    AccelStepper ** motors;
    Joint::Joint(double a_ratio,bool a_inverted,int a_homing_dir,int a_offset,int joint_num_steppers);
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
    void Joint::home(MultiStepper * m);

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
    AccelStepper ** motors;
    Sensor ** sensors;
    Arm::Arm(int n_joints);
    int num_motors;
    MultiStepper * steppers;
    Servo * gripper;
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
};


#endif