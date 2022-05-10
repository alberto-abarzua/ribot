
#include "Arduino.h"
#include "coms.h"
#include "arm.h"

Arm arm(6);
// Joint(double a_ratio,bool a_inverted,int a_homing_dir,int joint_num_steppers);
Joint j1(1,false,1,1);
Joint j2(1,false,1,2);
Joint j3(1,false,1,1);
Joint j4(1,false,1,1);
Joint j5(1,false,1,1);
Joint j6(1,false,1,1);



 void setup() {
  Serial.begin(9600);
  j1.create_motor(2,3);
  j2.create_motor(4,5);
  j2.create_motor(6,7);
  j3.create_motor(40,41);
  j4.create_motor(50,51);
  j5.create_motor(52,53);
  j6.create_motor(46,47);
  arm.register_joint(&j1);
  arm.register_joint(&j2);
  arm.register_joint(&j3);
  arm.register_joint(&j4);
  arm.register_joint(&j5);
  arm.register_joint(&j6);
  arm.build_joints();

}

void loop() {
  if(!run_reader()){
    char op = getOP();
    int code = getCode();
    int num_args =getNumArgs();
    long * args = getArgs();
    getM()->show();
    if (op == 'm'){
      if(code == 1){
        arm.add(args);
        Serial.print("SUCCES;");
      }
    }
    if(op == 'i'){
      if(code ==1){
        arm.show_pos();
        Serial.print("SUCCES;");

      }else if(code == 2){
        arm.show();
        Serial.print("SUCCES;");
      }
    }
    if(op == 'd'){
        arm.show();
        Serial.print("SUCCES;");


    }


  
  //getM()->show();
  
  }
  //arm.run();
}
