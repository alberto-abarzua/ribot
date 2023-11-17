using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Net.Sockets;
using System.Text;
using System;
using UnityEngine.UI;
using TMPro;
using NativeWebSocket;

using System.Runtime.InteropServices;
public class Controller : MonoBehaviour {

  [DllImport("__Internal")]
  private static extern int GetWebSocketPort();
  [DllImport("__Internal")]
  private static extern string GetWebSocketIp();
  [DllImport("__Internal")]
  private static extern string GetWebSocketProtocol();

  [DllImport("__Internal")]
  private static extern void PrintToConsole(string str);

  private static extern void SetWebSocketPort(int port);
  // Socket variables
  private WebSocket websocket = null;
  private int web_socket_port;
  private string web_socket_ip;
  private string web_socket_protocol;
  private float call_interval = 1f / 40f; // 40 Hz
  // last call timestamp
  private long last_call = 0;

  // Angles management
  private int[] inverted;
  private float[] current_angles;

  // Object variables
  private GameObject[] joints;
  private GameObject TCP;
  private TMP_Text TCP_location;
  private Text text_angles;

  public void Start() {

    // PrintToConsole("\n\nHello from Unity!\n\n");
    this.joints = new GameObject[6];

    for (int i = 0; i < 6; i++) {
      this.joints[i] = GameObject.Find("J" + (i + 1));
    }

    this.TCP = GameObject.Find("TCP");
    // this.text_angles = GameObject.Find("cur_angles").GetComponent < Text >
    // (); this.TCP_location = GameObject.Find("TCP_location").GetComponent <
    // TMP_Text > ();

    this.current_angles = new float[6];

    this.inverted = new int[] { 1, -1, -1, 1, -1, 1 };
    SetWebSocketInfo();
    this.SetupWebSocket();
    this.UpdateJoints();
    // InvokeRepeating(nameof(CallGetAngles), 0f, 0.03f); // CallGetAngles every
    // 0.1 seconds
  }

  public void SetWebSocketInfo() {
    string ip = GetWebSocketIp();
    int port = GetWebSocketPort();
    string protocol = GetWebSocketProtocol();
    this.web_socket_ip = ip;
    this.web_socket_port = port;
    this.web_socket_protocol = protocol;
    PrintToConsole("ip: " + this.web_socket_ip +
                   " port: " + this.web_socket_port +
                   " protocol: " + this.web_socket_protocol);
    // PrintToConsole("ip: " + web_socket_ip + " port: " + web_socket_port);
  }

  private void UpdateJoints() {
    for (int i = 0; i < 6; i++) {
      GameObject joint = joints[i];
      if (i == 0 || i == 3 || i == 5) {
        joint.transform.localEulerAngles =
            new Vector3(0, inverted[i] * this.current_angles[i], 0);

      } else if (i == 2) {
        joint.transform.localEulerAngles =
            new Vector3(inverted[i] * this.current_angles[i] - 90, 0, 0);
      } else {
        joint.transform.localEulerAngles =
            new Vector3(inverted[i] * this.current_angles[i], 0, 0);
      }
    }
    this.UpdateText();
  }

  private Tuple<int, int, int, float[]> ReadMessage(byte[] buf) {
    int op = (char)buf[0];
    // make the bitConverter little endian

    int code = BitConverter.ToInt32(buf, 1);
    int num_args = BitConverter.ToInt32(buf, 5);
    float[] args = new float[num_args];
    // Debug.Log("num_args: " + num_args);
    // Debug.Log("args: " + args);
    // Debug.Log("buf: " + buf);
    // Debug.Log("buf length: " + buf.Length);
    // Debug.Log("op: " + op);
    // Debug.Log("code: " +code);
    for (int i = 0; i < num_args; i++) {
      args[i] = BitConverter.ToSingle(
          buf, i * 4 + 9); // Use ToSingle for float values
    }
    return Tuple.Create(op, code, num_args, args);
  }

  private void CallGetAngles() {
    // Debug.Log("CallGetAngles");
    // show websocket state

    // Debug.Log("State: " + websocket.State.ToString());
    if (websocket.State == WebSocketState.Open) {
      long current_time = DateTimeOffset.Now.ToUnixTimeMilliseconds();
      if (current_time - this.last_call < this.call_interval * 1000) {
        return;
      }
      this.websocket.SendText("get_angles");
      this.last_call = DateTimeOffset.Now.ToUnixTimeMilliseconds();
    }
  }

  private float RadToDeg(float rad) { return (float)(rad * (180.0 / Math.PI)); }

  private void UpdateText() {
    Vector3 pos = TCP.transform.position;
    Vector3 ang = TCP.transform.eulerAngles;
    // this.TCP_location.text = String.Format("X: {0:0.##} Y: {1:0.##} Z:
    // {2:0.##}  A: {3:0.##} B: {4:0.##} C: {5:0.##}", pos[0], pos[1], pos[2],
    // ang[0], ang[1], ang[2]); this.text_angles.text =
    // String.Format("cur_angles
    // [{0:0.##},{1:0.##},{2:0.##},{3:0.##},{4:0.##},{5:0.##}]",
    // this.current_angles[0], this.current_angles[1], this.current_angles[2],
    // this.current_angles[3], this.current_angles[4], this.current_angles[5]);
  }

  private void SetupWebSocket() {

    // print this.web_socket_protocol;

    try {

      PrintToConsole("ip: " + this.web_socket_ip +
                     " port: " + this.web_socket_port +
                     " protocol: " + this.web_socket_protocol);

      this.websocket = new WebSocket(
          String.Format("{0}://{1}:{2}", this.web_socket_protocol,
                        this.web_socket_ip, this.web_socket_port));

      this.websocket.OnOpen += () => {
        // Debug.Log("Connection open!");
      };

      this.websocket.OnError += (e) => {
        // Debug.Log("Error! " + e);
        Invoke("SetupWebSocket", 5f);
      };

      this.websocket.OnClose += (e) => {
        // Debug.Log("Connection closed!");
        Invoke("SetupWebSocket", 5f);
      };

      this.websocket.OnMessage += (bytes) => {
        // Debug.Log("OnMessage!");
        string packedMessageString = BitConverter.ToString(bytes);
        // Debug.Log("Packed message: " + packedMessageString);
        // print length of bytes
        // Debug.Log(bytes.Length);
        (int op, int code, int numArgs, float[] args) = this.ReadMessage(bytes);
        for (int i = 0; i < 6; i++) {
          this.current_angles[i] = this.RadToDeg(args[i]);
        }
        this.UpdateJoints();
      };

      this.websocket.Connect();
    } catch (Exception e) {
      PrintToConsole("Error: " + e);
    }
  }

  private void Update() {

    if (this.websocket != null) {
#if !UNITY_WEBGL || UNITY_EDITOR
      this.websocket.DispatchMessageQueue();
#endif
      this.UpdateJoints();
      this.CallGetAngles();
    } else {
      PrintToConsole("Websocket is null");
      this.SetupWebSocket();
    }
  }
}
