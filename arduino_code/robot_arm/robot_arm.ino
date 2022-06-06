
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



void setup() {
  //Creation of arm and joints
  arm = new Arm(6);
  //Joint:: Joint(reduction ratio, inverted, homing_dir, offset,num_steppers, speed_multiplier);
  j1 = new Joint(11,false,1,(long)(-3501*(MICRO_STEPPING/8.0)),1,1.0);
  j2 = new Joint(5.357,false,-1,(long)(1400*(MICRO_STEPPING/8.0)),2,0.4);
  j3 = new Joint(4.5*5.0,true,-1,(long)(15183*(MICRO_STEPPING/8.0)),1,3.0);
  j4 = new Joint(1.0,true,-1,(long)(384*(MICRO_STEPPING/8.0)),1,1.0);
  j5 = new Joint(4.3,true,-1,(long)(1226*(MICRO_STEPPING/8.0)),1,0.6);
  j6 = new Joint(1.0,true,-1,(long)(763*(MICRO_STEPPING/8.0)),1,1.0);

  //Creation of motors.
  j1->create_motor(stepPin1,dirPin1);
  j2->create_motor(stepPin2,dirPin2);
  j2->create_motor(stepPin3,dirPin3);
  j3->create_motor(stepPin4,dirPin4);
  j4->create_motor(stepPin5,dirPin5);
  j5->create_motor(stepPin6,dirPin6);
  j6->create_motor(stepPin7,dirPin7);
  //Creation of sensors
  j1->create_sensor(hall_1);
  j2->create_sensor(hall_2);
  j3->create_sensor(hall_3);
  j4->create_sensor(hall_4);
  j5->create_sensor(hall_5);
  j6->create_sensor(hall_6);
  //Register joints to the arm.
  arm->register_joint(j1);
  arm->register_joint(j2);
  arm->register_joint(j3);
  arm->register_joint(j4);
  arm->register_joint(j5);
  arm->register_joint(j6);
  arm->create_gripper(gripper_pin);
  //Initialize arm,serial and ComsManager.
  Serial.begin(115200);
  arm->build_joints();
  com.init_coms(); // Initialize the variable for comManager.


  //Let the computer know we are ready.
  com.set_status(INITIALIZED);

}




//Main loop
void loop(){
  if(com.run_coms()){
    loop_message_handler(com.getCurrentMessage());
  }

  arm_check(); //Check pendind messages on run Queue.

}

/**
 * @brief Used to execute the messages received during operation. 
 * 
 * @param M New message to be executed.
 */
void loop_message_handler(Message * M){
    char op = M->op;
    int code =  M->code;
    long * args =  M->args;
    switch (op){

      case 'm': 
        switch (code){
          case 1: // Moves adding to the run queue
            com.addRunQueue(M);
            com.set_status(READY_STATUS);

            break;
          default:
            if(code>=10 && code <=15){
              arm->add_to_joint(code-10,M->args[0]);
              com.set_status(READY_STATUS);
            }
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
            if(code>=10 && code <=15){
                arm->home_joint(code-10);
                com.set_status(READY_STATUS);
              }
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
          default:
            arm->joints[code]->set_offset(args[0]);
            break;
        }
        break;
      default:
        break;
    }
}




/**
 * @brief Handles the first message M in the run queue. 
 * 
 * @param M Message to be executed or waited on.
 */
void run_queue_handler(Message *M){
    char op = M->op;
    int code = M->code;
    long * args = M->args;
    switch (op){
      case 'm': 
        switch (code){
          case 1: // Moves adding to the run queue
            if(arm->left_to_go()){ // Motors are still moving.

              bool same_dir = true;
              for (int i =0;i<arm->num_joins;i++){ // We check if the target direction is the same as the new message's direction.
                if (eq_sign(args[i],arm->l_positions[i])){
                  same_dir = false;
                }
              }   
              if(same_dir){ // If the direction is the same for all joints. We consume the message.
                com.popRunQueue();
                arm->add(args);
              }
            }else{ // Motors are at their target pos
              arm->add(args);
              com.popRunQueue();
            }

            break;
          default:
            break;
        }
        break;

      case 'g': 
        switch (code){
          case 1: // Moves adding to the run queue
            arm->set_gripper_angle(args[0]);
            com.popRunQueue();
            break;
          default:
            break;
        }
        break;
      default:
        com.popRunQueue();
        break;
    }
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
    run_queue_handler(com.peekRunQueue());
  }
  arm->run();
}