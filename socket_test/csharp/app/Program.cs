// See https://aka.ms/new-console-template for more information
using System;
using System.Net.Sockets;
using System.Text;  

class Test{
    private Socket s;
    private string ip;
    private int port;
    private int[] args;
    private char op;
    private int code;
    private int num_args;

    
    public Test(string ip,int port){
        this.ip = ip;
        this.port =port ;
        this.args = new Int32[7];
        this.s = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);  
    }
    /// <summary>
    /// Starts the socket.
    /// </summary>
    public void start(){
        //Conection and sending data
        int tries = 10;
        while(tries!=0){
            try{
             s.Connect(ip, port);
        }catch{
            Console.WriteLine("Reconecting");
            tries--;
        }
        }
        
       
    }

    /// <summary>
    /// Closes the socket.
    /// </summary>
    public void end(){
        s.Shutdown(SocketShutdown.Both);  
        s.Close();  
    }

    void read_message(byte[] buf){
        this.op = (char) buf[0];
        this.code = BitConverter.ToInt32(buf,1);
        this.num_args = BitConverter.ToInt32(buf,5); 
        for(int i=0;i< num_args ;i++){
            this.args[i] = BitConverter.ToInt32(buf,i*4+9);
        }
    }

    /// <summary>
    /// Receives data from socket, interprets it.
    /// </summary>
    public void run_socket(){   
        
                s.Send(BitConverter.GetBytes(0)); 



                byte[] bytesRec = new Byte[128];
                int num_bytes = s.Receive(bytesRec,bytesRec.Length,0);  //Receiving response
                if (num_bytes == 38){
                    this.read_message(bytesRec);
                    Console.WriteLine("{0}{1} [{2}]",this.op,this.code,string.Join(" ,",this.args)); 
                    s.Send(BitConverter.GetBytes(0)); 
                }
                     

                //Closing conection
            }


    
    public static void Main(){
        Test t = new Test("127.0.0.1",65433);
        t.start();
        while(true){
            t.run_socket();
            
        }
    }
}
 