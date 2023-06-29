using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class camera : MonoBehaviour
{
    
    public float speedH= 1.0f;
    public float speedV = 1.0f;
    private float yaw = 224.0f;
    private float pitch  = 23.0f;
    private bool locked = true;
    float move_speed = 800.0f;
    // Start is called before the first frame update
    void Start()
    {
        Screen.SetResolution(1280,780,false);
        Cursor.lockState = CursorLockMode.Locked;
        transform.position = new Vector3(309,627,346);
        Camera.main.aspect = 1f;
        
    }
    
    // Update is called once per frame
    void Update(){
        float vert =0;
        float hori =0;
        if (Input.GetKey("w")){
            vert = move_speed;
        }
        if (Input.GetKey("s")){
            vert = -move_speed;
        }
        if (Input.GetKey("a")){
            hori = -move_speed;
        }
        if (Input.GetKey("d")){
            hori = move_speed;
        }

        if(Input.GetKeyDown(KeyCode.Escape)){
            if (locked){
                Cursor.lockState = CursorLockMode.None;
            }else{
                Cursor.lockState = CursorLockMode.Locked;
            }
            locked = !locked;
            
        }
        
        transform.position += Camera.main.transform.forward*vert*Time.deltaTime + Camera.main.transform.right*hori*Time.deltaTime;
        if(locked){
            yaw += speedH*Input.GetAxis("Mouse X");
            pitch -= speedV*Input.GetAxis("Mouse Y");

            //the rotation range
            pitch = Mathf.Clamp(pitch, -60f, 90f);
            //the rotation range
            transform.eulerAngles = new Vector3(pitch,yaw,0.0f);
        }
       
    }
}
