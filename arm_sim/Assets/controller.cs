using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Net.Sockets;
using System.Text;  
using System;

public class controller : MonoBehaviour{


    private Socket s = null;
    private string ip;
    private int port;
    private int[] args;
    private char op;
    private int code;
    private int num_args;
    private float[] angles;
    private int acc =10000;

    private GameObject[] joints; //Joints
    private int[] inverted;
    // Start is called before the first frame update
    

    public void set_angles(){
        for(int i=0;i<6;i++){
            GameObject joint = joints[i];
            if (i==0|| i==3||i == 5){
                joint.transform.localEulerAngles = new Vector3(0,inverted[i]*this.angles[i],0);

            }else if(i==2){
                    joint.transform.localEulerAngles = new Vector3(inverted[i]*this.angles[i]-90,0,0);
            }
            else{
                joint.transform.localEulerAngles  = new Vector3(inverted[i]*this.angles[i],0,0);

            }
        }
    }
    



    void read_message(byte[] buf){
        this.op = (char) buf[0];
        this.code = BitConverter.ToInt32(buf,1);
        this.num_args = BitConverter.ToInt32(buf,5); 
        for(int i=0;i< num_args ;i++){
            this.args[i] = BitConverter.ToInt32(buf,i*4+9);
        }
    }
    public void update_angles(){
        for (int i =0;i<6;i++){
            this.angles[i] =(float) (((float)this.args[i]/(float)this.acc)/Math.PI)*(float)180.0;

        }
    }




    void Start(){
        joints = new GameObject[6];
        angles = new float[6];
        inverted = new int[] {1,-1,-1,1,-1,1};
        for (int i =0;i<6;i++){
            joints[i] = GameObject.Find("J"+(i+1));
            
        }
        this.s = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
        this.port = 65433;
        this.ip = "127.0.0.1";
        this.args = new Int32[7];
        int tries = 10;
        while(tries!=0){
            try{
             this.s.Connect(this.ip, this.port);
        }catch{
            Console.WriteLine("Reconecting");
            tries--;
        }
        }

    }

    // Update is called once per frame
    void Update(){
        if (this.s != null){
            this.s.Send(BitConverter.GetBytes(0)); 

            byte[] bytesRec = new Byte[128];
            int num_bytes = s.Receive(bytesRec,bytesRec.Length,0);  //Receiving response
            if (num_bytes == 38){
                this.read_message(bytesRec);
                this.update_angles();
                this.set_angles();
                Debug.Log(this.op+this.code+" ["+string.Join(" ,",this.angles)+ "]"); 
                this.s.Send(BitConverter.GetBytes(0)); 
            }
        }
       
                

    }
}
