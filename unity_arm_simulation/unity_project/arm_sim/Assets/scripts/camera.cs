using UnityEngine;

public class camera : MonoBehaviour
{
    public float speedH = 1.0f;
    public float speedV = 1.0f;
    private float yaw = 224.0f;
    private float pitch = 23.0f;
    float move_speed = 800.0f;
    private bool isCursorLocked = false; // Track if the cursor is locked

    void Start()
    {
        Screen.SetResolution(1280, 780, false);
        Cursor.lockState = CursorLockMode.None; // Do not lock the cursor initially
        Cursor.visible = true; // Make the cursor visible
        yaw = transform.eulerAngles.y; //set current position
        pitch = transform.eulerAngles.x;
        //set current position
    }

    void Update()
    {
        // Check for a left mouse button click and lock the cursor if it's currently unlocked
        // Debug.Log(transform.position);

        if (Input.GetMouseButtonDown(0) && Cursor.lockState == CursorLockMode.None)
        {
            Cursor.lockState = CursorLockMode.Locked;
            isCursorLocked = true; // Set the tracking variable
        }

        // Check for Escape key press and toggle the cursor lock state
        if (Input.GetKeyDown(KeyCode.Escape))
        {
            isCursorLocked = !isCursorLocked; // Toggle the tracking variable
            Cursor.lockState = isCursorLocked ? CursorLockMode.Locked : CursorLockMode.None;
        }

        // Allow camera movement only when the cursor is locked
        if (isCursorLocked)
        {
            float vert = Input.GetKey("w") ? move_speed : Input.GetKey("s") ? -move_speed : 0;
            float hori = Input.GetKey("a") ? -move_speed : Input.GetKey("d") ? move_speed : 0;

            transform.position += Camera.main.transform.forward * vert * Time.deltaTime + Camera.main.transform.right * hori * Time.deltaTime;

            yaw += speedH * Input.GetAxis("Mouse X");
            pitch -= speedV * Input.GetAxis("Mouse Y");

            // The rotation range
            pitch = Mathf.Clamp(pitch, -60f, 90f);

            // The rotation range
            transform.eulerAngles = new Vector3(pitch, yaw, 0.0f);
        }
    }
}
