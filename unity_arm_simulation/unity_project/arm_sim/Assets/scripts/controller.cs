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
  private float tool_value = 0f;

  // Object variables
  private GameObject[] joints;
  private GameObject TCP;
  private GameObject Gripper1;
  private GameObject Gripper2;
  private Vector3 initialPositionGripper1;
  private Vector3 initialPositionGripper2;
  private TMP_Text TCP_location;
  private Text text_angles;

  public void Start() {

    // PrintToConsole("\n\nHello from Unity!\n\n");
    this.joints = new GameObject[6];

    for (int i = 0; i < 6; i++) {
      this.joints[i] = GameObject.Find("J" + (i + 1));
    }

    this.TCP = GameObject.Find("TCP");
    this.Gripper1 = GameObject.Find("grip_1");
    this.Gripper2 = GameObject.Find("grip_2");

    this.initialPositionGripper1 = Gripper1.transform.localPosition;
    this.initialPositionGripper2 = Gripper2.transform.localPosition;

    this.current_angles = new float[6];

    this.inverted = new int[] { 1, -1, -1, 1, -1, 1 };
    SetWebSocketInfo();
    this.SetupWebSocket();
    this.UpdateJoints();
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

    float maxDistance = 60f;

    float tool_value = Mathf.Clamp(this.tool_value / (Mathf.PI / 2f), 0f, 1f);

    float zDistance = maxDistance * (1 - tool_value);

    zDistance = maxDistance - zDistance;

    // PrintToConsole("tool_value: " + tool_value + " zDistance: " + zDistance);

    if (Gripper1 != null) {

      Gripper1.transform.localPosition =
          new Vector3(initialPositionGripper1.x, initialPositionGripper1.y,
                      initialPositionGripper1.z + zDistance / 2);

      // PrintToConsole("Gripper1: " + Gripper1.transform.localPosition);
    }

    if (Gripper2 != null) {

      Gripper2.transform.localPosition =
          new Vector3(initialPositionGripper2.x, initialPositionGripper2.y,
                      initialPositionGripper2.z - zDistance / 2);
      // PrintToConsole("Gripper2: " + Gripper2.transform.localPosition);
    }
  }

  private Tuple<int, int, int, float[]> ReadMessage(byte[] buf) {
    int op = (char)buf[0];

    int code = BitConverter.ToInt32(buf, 1);
    int num_args = BitConverter.ToInt32(buf, 5);
    float[] args = new float[num_args];
    for (int i = 0; i < num_args; i++) {
      args[i] = BitConverter.ToSingle(buf, i * 4 + 9);
    }

    return Tuple.Create(op, code, num_args, args);
  }

  private void CallGetAngles() {

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

  private void SetupWebSocket() {

    try {

      PrintToConsole("ip: " + this.web_socket_ip +
                     " port: " + this.web_socket_port +
                     " protocol: " + this.web_socket_protocol);

      if (this.web_socket_protocol == "wss") {
        this.websocket = new WebSocket(String.Format(
            "{0}://{1}", this.web_socket_protocol, this.web_socket_ip));
      } else {
        this.websocket = new WebSocket(
            String.Format("{0}://{1}:{2}", this.web_socket_protocol,
                          this.web_socket_ip, this.web_socket_port));
      }

      this.websocket.OnOpen += () => {};

      this.websocket.OnError += (e) => { Invoke("SetupWebSocket", 5f); };

      this.websocket.OnClose += (e) => { Invoke("SetupWebSocket", 5f); };

      this.websocket.OnMessage += (bytes) => {
        string packedMessageString = BitConverter.ToString(bytes);
        (int op, int code, int numArgs, float[] args) = this.ReadMessage(bytes);
        for (int i = 0; i < 6; i++) {
          this.current_angles[i] = this.RadToDeg(args[i]);
        }

        this.tool_value = args[6];

        // PrintToConsole("op: " + op + " code: " + code + " numArgs: " +
        // numArgs +
        //                " args: " + args[0] + " " + args[1] + " " + args[2] +
        //                " " + args[3] + " " + args[4] + " " + args[5] + " " +
        //                args[6]);

        this.UpdateJoints();
      };

      this.websocket.Connect();

    } catch (Exception e) {
      PrintToConsole("websocket info " + this.web_socket_ip + " " +
                     this.web_socket_port + " " + this.web_socket_protocol);
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
