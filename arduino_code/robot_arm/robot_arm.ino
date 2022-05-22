
#include "Arduino.h"
#include "coms.h"
#include "arm.h"

/**
 * @brief author Alberto Abarzua
 * 
 */

//Serial Manager

ComsManager com;

Arm * arm;

Joint * j1;
Joint * j2;
Joint * j3;
Joint * j4;
Joint * j5;
Joint * j6;

// Motor 1
const int dirPin1 = 8;
const int stepPin1 = 9;
// Motor 2
const int dirPin2 = 10;
const int stepPin2 = 11;
// Motor 3
const int dirPin3=32;
const int stepPin3 =33;
// Motor 4
const int dirPin4 = 34;
const int stepPin4 = 35;
// Motor 5
const int dirPin5 = 36;
const int stepPin5 = 37;
//Motor 6
const int dirPin6 = 38;
const int stepPin6 = 39;
//Motor 7
const int dirPin7 = 40;
const int stepPin7 = 41;

// Joint 1
const int hall_1 = 7;
const int hall_2 = 6;
const int hall_3 = 5;
const int hall_4 = 4;
const int hall_5 = 3;
const int hall_6 = 2;

const int gripper_pin = 12;

const int offsets[] = {-3234*(MICRO_STEPPING/8),-1250*(MICRO_STEPPING/8),(-5186+8998)*(MICRO_STEPPING/8),-435*(MICRO_STEPPING/8),-566*(MICRO_STEPPING/8),-75*(MICRO_STEPPING/8)}; // Offsets of each joint in steps



void setup() {
  Serial.begin(115200);
  arm = new Arm(6);
  //Joint:: Joint(double a_ratio,bool a_inverted,int a_homing_dir,int a_offset,int joint_num_steppers,double a_speed_multiplier);
  j1 = new Joint(9.3,false,1,(long)(-6468*(MICRO_STEPPING/16.0)),1,4.0);
  j2 = new Joint(5.357,false,1,(long)(-2500*(MICRO_STEPPING/16.0)),2,5.0);
  j3 = new Joint(4.5*5.0,true,1,(long)(10321*(MICRO_STEPPING/16.0)),1,5.0);
  j4 = new Joint(1.0,true,-1,(long)(-670*(MICRO_STEPPING/16.0)),1,15.0);
  j5 = new Joint(3.5,true,1,(long)(-1132*(MICRO_STEPPING/16.0)),1,5.0);
  j6 = new Joint(1.0,true,-1,(long)(-1700*(MICRO_STEPPING/16.0)),1,15.0);
  j1->create_motor(stepPin1,dirPin1);
  j2->create_motor(stepPin2,dirPin2);
  j2->create_motor(stepPin3,dirPin3);
  j3->create_motor(stepPin4,dirPin4);
  j4->create_motor(stepPin5,dirPin5);
  j5->create_motor(stepPin6,dirPin6);
  j6->create_motor(stepPin7,dirPin7);
  j1->create_sensor(hall_1);
  j2->create_sensor(hall_2);
  j3->create_sensor(hall_3);
  j4->create_sensor(hall_4);
  j5->create_sensor(hall_5);
  j6->create_sensor(hall_6);
  arm->register_joint(j1);
  arm->register_joint(j2);
  arm->register_joint(j3);
  arm->register_joint(j4);
  arm->register_joint(j5);
  arm->register_joint(j6);
  arm->create_gripper(gripper_pin);
  arm->build_joints();
  com.init_coms(); // Initialize the variable for comManager.
  com.set_status(INITIALIZED);
  

}

void arm_check();



void loop(){
  if(com.run_coms()){
    //Get the info from the message:
    Message * M = com.getCurrentMessage();
    char op = M->op;
    int code =  M->code;
    int numArgs =  M->num_args;
    long * args =  M->args;
    switch (op){

      case 'm': 
        switch (code){
          case 1:
            com.addRunQueue(M);
            com.set_status(READY_STATUS);

            break;
          default:
            com.set_status(UNK);
            break;
        }
        break;

      case 'i':
        switch (code){
          case 1:
            arm->show_pos();
            com.set_status(PRINTED);

            
            break;
          case 2:
            arm->show();

            com.set_status(PRINTED);
            break;
          case 3:
            arm->show_sensors();

            com.set_status(PRINTED);
            break;
          case 4:
            com.show_queues();

            com.set_status(PRINTED);
            break;
          case 5:
            arm->show_gripper();
            
            com.set_status(PRINTED);

            break;
          case 6:
            arm->show_offsets();
            com.set_status(PRINTED);

            break;
          default:

            com.set_status(UNK);
            break;
        }
        break;

      case 'h':
        switch (code){
          case 0:
            arm->home();

            com.set_status(READY_STATUS);
            
            break;
          default:
            arm->home_joint(code);
            com.set_status(READY_STATUS);
            break;
        }
        break;

      case 'g':
        switch (code){
          case 1:
            com.addRunQueue(M);
            com.set_status(READY_STATUS);
            
            break;
          default:
            com.set_status(UNK);
            break;
        }
        break;

      case 'o':
        switch (code){
          case 1:
            break;

          default:
            arm->joints[code]->set_offset(args[0]);
            break;
        }
        break;
        

      default:
        break;
    }
  }

  arm_check(); // Runs the checks to run pending messages.

}


/**
 * @brief Checks if two numbers have the same sign.
 * 
 * @param num1 first number
 * @param num2 second number
 * @return true if their signs are equal
 * @return false if signs are not the same
 */
bool eq_sign(long num1,long num2){
  return (num1^ num2) >= 0;
}

/**
 * @brief Checks if there are pending messages to be executed and runs them.
 * 
 */
void arm_check(){
  if (!com.isEmptyRunQueue()){ //There are moves in the move queue
    if(arm->left_to_go()){//Motors are still moving
      Message * new_M = com.peekRunQueue();
      if (new_M->op == 'm' && new_M->code == 1){
        bool same_dir = true;
        for (int i =0;i<arm->num_joins;i++){
          if (eq_sign(new_M->args[i],arm->l_positions[i])){
            same_dir = false;
          }
        }
        if(same_dir){
          com.popRunQueue();
          arm->add(new_M->args);
        }
      }
      
    }else{//Motors have reached their positions.
      Message * new_M = com.popRunQueue();
      if(new_M->op == 'g' && new_M->code == 1){
          arm->set_gripper_angle(new_M->args[0]);
     }
      else if(new_M->op == 'm' && new_M->code == 1){
        arm->add(new_M->args);
      }
    }
    
  }
  arm->run();
}