
#include "Arduino.h"
#include "coms.h"
#include "arm.h"

Arm * arm;
Joint * j1;
Joint * j2;
Joint * j3;
Joint * j4;
Joint * j5;
Joint * j6;

// Motor 1
const int stepPin1 = 52;
const int dirPin1 = 53;
// Motor 2
const int stepPin2 = 51;
const int dirPin2 = 50;
// Motor 3
const int stepPin3 =49;
const int dirPin3=48;
// Motor 4
const int stepPin4 = 47;
const int dirPin4 = 46;
// Motor 5
const int stepPin5 = 45;
const int dirPin5 = 44;
//Motor 6
const int stepPin6 = 43;
const int dirPin6 = 42;
//Motor 7
const int stepPin7 = 10;
const int dirPin7 = 11;

// Joint 1
const int hall_1 = 7;
const int hall_2 = 6;
const int hall_3 = 5;
const int hall_4 = 4;
const int hall_5 = 3;
const int hall_6 = 2;

const int gripper_pin = 8;

const int offsets[] = {-3234*(MICRO_STEPPING/8),-1250*(MICRO_STEPPING/8),(-5186+8998)*(MICRO_STEPPING/8),-435*(MICRO_STEPPING/8),-566*(MICRO_STEPPING/8),-75*(MICRO_STEPPING/8)}; // Offsets of each joint in steps



void setup() {
  Serial.begin(115200);
  arm = new Arm(6);
  // Joint(double a_ratio,bool a_inverted,int a_homing_dir,int joint_num_steppers);
  j1 = new Joint(9.3,true,1,-3234*(MICRO_STEPPING/8),1);
  j2 = new Joint(5.357,false,1,-1250*(MICRO_STEPPING/8),2);
  j3 = new Joint(4.5*5.0,false,1,(-5186+8998)*(MICRO_STEPPING/8),1);
  j4 = new Joint(1.0,false,1,-435*(MICRO_STEPPING/8),1);
  j5 = new Joint(3.5,true,-1,-566*(MICRO_STEPPING/8),1);
  j6 = new Joint(1.0,false,-1,-75*(MICRO_STEPPING/8),1);
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
  init_coms();
  set_status(INITIALIZED);
  

}

void loop() {
  run_reader();
  if(!new_data()){
    //Get the info from the message:
    Message * M = getM();
    bool should_return = true;
    char op = M->op;
    int code =  M->code;
    int numArgs =  M->num_args;
    long * args =  M->args;
    switch (op){

      case 'm': 
        switch (code){
          case 1:
            queueMove(M);
            should_return = false;
            set_status(READY_STATUS);

            break;
          default:
            set_status(UNK);
            break;
        }
        break;

      case 'i':
        switch (code){
          case 1:
            arm->show_pos();
            set_status(PRINTED);

            
            break;
          case 2:
            arm->show();

            set_status(PRINTED);
            break;
          case 3:
            arm->show_sensors();

            set_status(PRINTED);
            break;
          case 4:
            show_queues();

            set_status(PRINTED);
            break;
          default:

            set_status(UNK);
            break;
        }
        break;

      case 'h':
        switch (code){
          case 0:
            arm->home();

            set_status(READY_STATUS);
            
            break;
          default:

            set_status(UNK);
            break;
        }
        break;

      case 'g':
        switch (code){
          case 1:
          
            arm->set_gripper_angle(args[0]);

            set_status(READY_STATUS);
            break;
          default:
            set_status(UNK);
            break;
        }
        break;

      case 's':
        switch (code){
          case 1:
            toggle_debug();
            break;
          case 2:

            break;
          default:

            break;
        }
        break;
        

      default:
        break;
    }


    if(should_return){
      returnM(M);
    }

  }
  check_busy();
  if (!arm->left_to_go() && movesOnQueue()){//Motors have reached positions.
    Message * new_M = unqueueMove();
    arm->add(new_M->args);
    returnM(new_M);
  }
  arm->run();

}
