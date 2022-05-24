using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class controll : MonoBehaviour{   

     GameObject GetChildWithName(GameObject obj, string name) {
        Transform trans = obj.transform;
        Transform childTrans = trans. Find(name);
        if (childTrans != null) {
            return childTrans.gameObject;
        } else {
            return null;
        }
    }
    // Start is called before the first frame update
    void Start(){
        GameObject j1 = GameObject.Find("J1");
        Debug.Log(j1.name);
    }
    // Update is called once per frame
    void Update(){
        
    }
}
