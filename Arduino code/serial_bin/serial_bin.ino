
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

 void setup() {
  Serial.begin(115200);
  arm = new Arm(6);
  // Joint(double a_ratio,bool a_inverted,int a_homing_dir,int joint_num_steppers);
  j1 = new Joint(1,false,1,1);
  j2 = new Joint(1,false,1,2);
  j3 = new Joint(1,false,1,1);
  j4 = new Joint(1,false,1,1);
  j5 = new Joint(1,false,1,1);
  j6 = new Joint(1,false,1,1);
  j1->create_motor(43,44);
  j2->create_motor(4,5);
  j2->create_motor(6,7);
  j3->create_motor(40,41);
  j4->create_motor(50,51);
  j5->create_motor(52,53);
  j6->create_motor(46,47);
  arm->register_joint(j1);
  arm->register_joint(j2);
  arm->register_joint(j3);
  arm->register_joint(j4);
  arm->register_joint(j5);
  arm->register_joint(j6);
  arm->build_joints();
  init_coms();
  Serial.write(INITIALIZED);

}

void loop() {
  if(!run_reader()){
    //Get the info from the message:
    char op = getOP();
    int code = getCode();
    int numArgs = getNumArgs();
    long * args = getArgs();
    
    switch (op){

      case 'm':
        switch (code){
          case 1:
            arm->add(args);
            set_status(READY_STATUS);
            break;
          default:
            break;
        }
        break;
      case 'i':
        switch (code){
          case 1:
            arm->show_pos();
            break;
          case 2:
            arm->show();
            break;
          default:
            break;
        }
        break;


      default:
        break;
    }



  }
}
