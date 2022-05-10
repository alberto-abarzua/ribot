#ifndef arm_h
#define arm_h
#include <AccelStepper.h>
#include <MultiStepper.h>
#include <Servo.h>



class Sensor{
  private:
    int pin;
  public:
    Sensor(int new_pin);
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
    Joint::Joint(double a_ratio,bool a_inverted,int a_homing_dir);
    Joint::Joint(double a_ratio,bool a_inverted,int a_homing_dir,int joint_num_steppers);
    void Joint::create_motor(int step_pin,int dir_pin);
    void Joint::create_sensor(int pin);
    void Joint::show();
    void Joint::motor_setup();
    void Joint::add_angle(long val);


};




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
    MultiStepper steppers;
    Servo gripper;
    void Arm::register_joint(Joint* joint);
    void Arm::build_joints();
    void Arm::show();
    void Arm::create_gripper(int pin);
    void Arm::run();
    void Arm::add(long * args);
    void Arm::show_pos();
};


#endif