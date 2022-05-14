#include "coms.h"




//Global vars
char status;
long ** ARGS;
bool NEW_DATA;
byte * BUF;
int max_val;
bool DEBUG;
ArduinoQueue<Message*> * q_fresh; //Queue to store unused messages.
ArduinoQueue<Message*> * q_in; // Queue to store messages that need to be executed.
ArduinoQueue<Message*> * q_motor; // Motor instruct queue.

Message ** Ms;
void init_coms(){
   BUF =(byte *) malloc(sizeof(byte)*READING_BUFFER_SIZE);
   ARGS = (long **) malloc(sizeof(long *)*MESSAGE_BUFFER_SIZE);
   q_fresh = new  ArduinoQueue<Message*>(MESSAGE_BUFFER_SIZE);
   q_in = new  ArduinoQueue<Message*>(4);
   q_motor = new  ArduinoQueue<Message*>(MESSAGE_BUFFER_SIZE);
   max_val = 0;

   for(int i=0;i<MESSAGE_BUFFER_SIZE;i++){
      ARGS[i] = (long *)malloc(sizeof(long)*MAX_ARGS);
      Message * m = new Message(ARGS[i]);
      q_fresh->enqueue(m);
   }
   DEBUG = false;
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

void toggle_debug(){
   DEBUG = !DEBUG;
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


bool run_reader(){
   NEW_DATA = true;
   my_read(BUF,READING_BUFFER_SIZE,&NEW_DATA);//Reads the char from serial
   if(!NEW_DATA){
      Message * m_clean =  q_fresh->dequeue();//Get an unused message

      getMessage(BUF,m_clean); //New message is complete

      q_in->enqueue(m_clean);

   }
   return NEW_DATA;
}

bool new_data(){
   return q_in->isEmpty();
}


Message * peekM(){
   Message * M = q_in->getHead();
   return M;
}
Message * getM(){ // Gets the first message from the message buffer.
   int c = q_in->itemCount();
   if (c>max_val){
      max_val = c;
   }
   Message * M = q_in->dequeue();
   return M;
}

void returnM(Message * M){
   q_fresh->enqueue(M);
}
bool can_receive(){
   return ((q_in->itemCount() <= 2) && (q_motor->itemCount() <= MESSAGE_BUFFER_SIZE-10) && (q_fresh->itemCount() >=5));
}

void set_status(char new_status){
   status = can_receive() ? new_status : BUSY;
   if (status == BUSY ||  status == CONTINUE || status == PRINTED || status == INITIALIZED || status == CONTINUE){
      Serial.write(status);
   }
   
}

void queueMove(Message *m){
   q_motor->enqueue(m);
}

void show_queues(){
   Serial.print("q_fresh: ");
   Serial.print(q_fresh->itemCount());
   Serial.print(" q_in: ");
   Serial.print(q_in->itemCount());
   Serial.print(" q_motor: ");
   Serial.print(q_motor->itemCount());
   Serial.print(" max val: ");
   Serial.print(max_val);


}

Message * unqueueMove(){
   return q_motor->dequeue();
}

bool movesOnQueue(){
   return !q_motor->isEmpty();
}

bool almostEmpty(){
   return (q_in->itemCount() <=5) && (q_motor->itemCount() <=5);
}
void check_busy(){
   if (status == BUSY && almostEmpty()){
      set_status(CONTINUE);

   }
}

Message * peekNextMove(){
   return q_motor->getHead();
}
/**
-----------------------------
-----------     Message     -----------
-----------------------------

 */


Message::Message(long*nargs){
    op = ' ';
    code =0;
    num_args = 0;
    args = nargs;
    viewed = false;
  }

void Message::rebuild(char nop,long ncode,long *nargs,int nnum_args){
    op = nop;
    code =ncode;
    num_args = nnum_args;
    viewed = false;
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
     Serial.print(" )");
  }






