using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Net.Sockets;
using System.Text;
using System;
using UnityEngine.UI;
using TMPro;
using NativeWebSocket;

public class controller: MonoBehaviour {

    // Socket variables
    private WebSocket websocket = null;
    private int web_socket_port;
    private string web_socket_ip ;

    // Angles management
    private int[] inverted;
    private float[] current_angles;

    // Object variables
    private GameObject[] joints;
    private GameObject TCP;
    private TMP_Text TCP_location;
    private Text text_angles;

    public void Start() {

        this.joints = new GameObject[6];

        for (int i = 0; i < 6; i++) {
            this.joints[i] = GameObject.Find("J" + (i + 1));
        }

        this.TCP = GameObject.Find("TCP");
        // this.text_angles = GameObject.Find("cur_angles").GetComponent < Text > ();
        // this.TCP_location = GameObject.Find("TCP_location").GetComponent < TMP_Text > ();

        this.current_angles = new float[6];

        this.inverted = new int[] {
            1,
            -1,
            -1,
            1,
            -1,
            1
        };

        Application.ExternalEval("GetWebSocketInfo();");
        this.SetupWebSocket();
        this.UpdateJoints();
        InvokeRepeating(nameof(CallGetAngles), 0f, 0.4f); // CallGetAngles every 0.1 seconds

    }

    public void SetWebSocketInfo(string info) {
        string[] parts = info.Split(':');
        web_socket_ip = parts[0];
        web_socket_port = int.Parse(parts[1]);
    }

    private void UpdateJoints() {
        for (int i = 0; i < 6; i++) {
            GameObject joint = joints[i];
            if (i == 0 || i == 3 || i == 5) {
                joint.transform.localEulerAngles = new Vector3(0, inverted[i] * this.current_angles[i], 0);

            } else if (i == 2) {
                joint.transform.localEulerAngles = new Vector3(inverted[i] * this.current_angles[i] - 90, 0, 0);
            } else {
                joint.transform.localEulerAngles = new Vector3(inverted[i] * this.current_angles[i], 0, 0);

            }
        }
        this.UpdateText();

    }

    private Tuple < int, int, int, float[] > ReadMessage(byte[] buf) {
        int op = (char) buf[0];
        // make the bitConverter little endian

        int code = BitConverter.ToInt32(buf, 1);
        int num_args = BitConverter.ToInt32(buf, 5);
        float[] args = new float[num_args];
        Debug.Log("num_args: " + num_args);
        Debug.Log("args: " + args);
        Debug.Log("buf: " + buf);
        Debug.Log("buf length: " + buf.Length);
        Debug.Log("op: " + op);
        Debug.Log("code: " +code);
        for (int i = 0; i < num_args; i++) {
            args[i] = BitConverter.ToSingle(buf, i * 4 + 9); // Use ToSingle for float values
        }
        return Tuple.Create(op, code, num_args, args);
    }

    private void CallGetAngles() {
        Debug.Log("CallGetAngles");
        // show websocket state
        Debug.Log("State: " + websocket.State.ToString());
        if (websocket.State == WebSocketState.Open){
        this.websocket.SendText("get_angles");

        }

    }

    private float RadToDeg(float rad) {
        return (float)(rad * (180.0 / Math.PI));
    }

    private void UpdateText() {
        Vector3 pos = TCP.transform.position;
        Vector3 ang = TCP.transform.eulerAngles;
        // this.TCP_location.text = String.Format("X: {0:0.##} Y: {1:0.##} Z: {2:0.##}  A: {3:0.##} B: {4:0.##} C: {5:0.##}", pos[0], pos[1], pos[2], ang[0], ang[1], ang[2]);
        // this.text_angles.text = String.Format("cur_angles [{0:0.##},{1:0.##},{2:0.##},{3:0.##},{4:0.##},{5:0.##}]", this.current_angles[0], this.current_angles[1], this.current_angles[2], this.current_angles[3], this.current_angles[4], this.current_angles[5]);
    }

    private void SetupWebSocket() {

        this.websocket = new WebSocket(String.Format("ws://{0}:{1}", this.web_socket_ip, this.web_socket_port));

        this.websocket.OnOpen += () => {
            Debug.Log("Connection open!");
        };

        this.websocket.OnError += (e) => {
            Debug.Log("Error! " + e);
             Invoke("SetupWebSocket", 5f);
        };

        this.websocket.OnClose += (e) => {
            Debug.Log("Connection closed!");
            Invoke("SetupWebSocket", 5f);
        };

        this.websocket.OnMessage += (bytes) => {
                Debug.Log("OnMessage!");
                string packedMessageString = BitConverter.ToString(bytes);
                Debug.Log("Packed message: " + packedMessageString);
                //print length of bytes
                Debug.Log(bytes.Length);
                (int op, int code, int numArgs, float[] args) = this.ReadMessage(bytes);
                for (int i = 0; i < 6; i++) {
                    this.current_angles[i] = this.RadToDeg(args[i]);
                }
                this.UpdateJoints();
            };

        this.websocket.Connect();

    }

    private void Update() {

        if (this.websocket != null) {
            #if!UNITY_WEBGL || UNITY_EDITOR
            this.websocket.DispatchMessageQueue();
            #endif
            this.UpdateJoints();

        }

    }
}