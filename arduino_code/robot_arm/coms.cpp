#include "coms.h"


/**
 * @brief author Alberto Abarzua
 * 
 */



/**
-----------------------------
-----------     ComsManager     -----------
-----------------------------

 */


ComsManager::init_coms(){
   BUF =(byte *) malloc(sizeof(byte)*READING_BUFFER_SIZE);
   q_fresh = new  ArduinoQueue<Message*>(MESSAGE_BUFFER_SIZE);
   q_run = new  ArduinoQueue<Message*>(MESSAGE_BUFFER_SIZE);
   for(int i=0;i<MESSAGE_BUFFER_SIZE;i++){ //We create the messages
      long * arg = (long *)malloc(sizeof(long)*MAX_ARGS);
      Message * m = new Message(arg);
      q_fresh->enqueue(m);
   }
}

long ComsManager::get_long(byte * buf,int offset){
    long res = 0;
    res |= ((long) buf[offset+3]<<24);
    res |= ((long) buf[offset+2]<<16);
    res |= ((long) buf[offset+1]<<8);
    res |= ((long) buf[offset+0]);
    return res;
}

void ComsManager::printBuf(byte * buf,int num){
   Serial.print("reading buf: ");
   for (int i =0;i<num;i++){
      Serial.print(" - ");
      Serial.print((char) buf[i]);
   }
   Serial.println("||");
}



void ComsManager::getMessage(Message *m){
   char op = (char)BUF[0];
   long code= get_long(BUF,1);
   int num_args = get_long(BUF,5);
   long args[num_args];
   int offset = 9;
   for (int i=0;i<num_args;i++){
      args[i] = get_long(BUF,offset);
      offset+=4;
   }
   m->rebuild(op,code,args,num_args);
   return m;
}

void ComsManager::read(){
  bool reading = true;
  int static idx = 0;
  byte read_byte;
  while(Serial.available()> 0){
    NEW_DATA = true;
    read_byte = Serial.read();
    
    if((char) read_byte == ';' || idx == READING_BUFFER_SIZE-1){
      BUF[idx] = '\0';
      idx= 0;
      NEW_DATA = false;
      break;
    }else{
      BUF[idx] = read_byte;
      idx ++;
    }
  }
}


bool ComsManager::run_coms(){
   NEW_DATA = true;
   read();//Reads from serial
   if(!NEW_DATA){
      cur_message =  q_fresh->dequeue();//Get an unused message
      getMessage(cur_message); //New message is complete
   }
   check_busy();
   return !NEW_DATA;
}


Message * ComsManager::getCurrentMessage(){
   return cur_message;
}


bool ComsManager::can_receive(){
   int tolerance = 10;
   return (q_run->itemCount() <= MESSAGE_BUFFER_SIZE-tolerance);
}

void ComsManager::set_status(char new_status){
   status = can_receive() ? new_status : BUSY;
   if (status == BUSY ||  status == CONTINUE || status == PRINTED || status == INITIALIZED || status == CONTINUE){
      Serial.write(status);
   }
   
}

void ComsManager::addRunQueue(Message *m){
   q_run->enqueue(m);
}

void ComsManager::show_queues(){
   Serial.print("q_fresh: ");
   Serial.print(q_fresh->itemCount());
   Serial.print(" q_run: ");
   Serial.print(q_run->itemCount());
}

Message * ComsManager::peekRunQueue(){
   return q_run->getHead();
}

Message * ComsManager::popRunQueue(){
   Message * m = q_run->dequeue();
   q_fresh->enqueue(m); //Return it to the unused messages queue
   return m;
}

bool ComsManager::isEmptyRunQueue(){
   return q_run->isEmpty();
}

bool ComsManager::almostEmpty(){
   int tolerance = 5;
   return (q_run->itemCount() <=tolerance);
}


void ComsManager::check_busy(){
   if (status == BUSY && almostEmpty()){
      set_status(CONTINUE);

   }
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
     Serial.print(" )");
  }






