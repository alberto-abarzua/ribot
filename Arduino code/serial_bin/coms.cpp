#include "Arduino.h"
#include "coms.h"

//Global vars
const int MAX_SIZE = 512;
const int MAX_ARGS = 32;
long ARGS[MAX_ARGS];
bool NEW_DATA;
Message M(ARGS);
byte BUF[MAX_SIZE];



Message::Message(char nop,long ncode,long *nargs,int nnum_args){
    op = nop;
    code =ncode;
    num_args = nnum_args;
    for (int i =0;i<num_args;i++){
       args[i] = nargs[i];
    }
  }


Message::Message(long*nargs){
    op = ' ';
    code =0;
    num_args = 0;
    args = nargs;
  }

void Message::rebuild(char nop,long ncode,long *nargs,int nnum_args){
    op = nop;
    code =ncode;
    num_args = nnum_args;
    for (int i =0;i<num_args;i++){
       args[i] = nargs[i];
    }
  }

void Message::show(){
    Serial.print("Message: ");
    Serial.print("Op: ");
    Serial.print(op);
    Serial.print(code);
    Serial.print(" args ( ");
    
    for(int i =0;i<num_args;i++){
       Serial.print(" <=> ");
        Serial.print(args[i]);  
     }
     Serial.println(" )");
  }

long get_long(byte * buf,int offset){
    long res = 0;
    res |= ((long) buf[offset+3]<<24);
    res |= ((long) buf[offset+2]<<16);
    res |= ((long) buf[offset+1]<<8);
    res |= ((long) buf[offset+0]);
    return res;
}

void printBuf(byte * buf,int num){
   Serial.print("reading buf: ");
   for (int i =0;i<num;i++){
      Serial.print(" - ");
      Serial.print((char) buf[i]);
   }
   Serial.println("||");
}

void my_read(byte * buf,int max_size,bool* newData){
  bool reading = true;
  int static idx = 0;
  byte read_byte;
  while(Serial.available()> 0){
    *newData = true;
    read_byte = Serial.read();
    
    if((char) read_byte == ';' || idx == max_size-1){
      buf[idx] = '\0';
      idx= 0;
      *newData = false;
      break;
    }else{
      buf[idx] = read_byte;
      idx ++;
    }
  }
}

void getMessage(byte * buf,Message *m){
   char op = (char)buf[0];
   long code= get_long(buf,1);
   int num_args = get_long(buf,5);
   long args[num_args];
   int offset = 9;
   for (int i=0;i<num_args;i++){
      args[i] = get_long(buf,offset);
      offset+=4;
   }
   m->rebuild(op,code,args,num_args);
   return m;
}

bool run_reader(){
   NEW_DATA = true;
   my_read(BUF,MAX_SIZE,&NEW_DATA);//Reads the char from serial
   if(!NEW_DATA){
      getMessage(BUF,&M);
   }
   return NEW_DATA;
}

bool new_data(){
   return NEW_DATA;
}
Message * getM(){
   return &M;
}

char getOP(){
   return M.op;
}

int getCode(){
   return M.code;
}

long * getArgs(){
   return M.args;
}

int getNumArgs(){
   return M.num_args;
}
