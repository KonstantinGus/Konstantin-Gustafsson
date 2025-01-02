using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CoreHandler : MonoBehaviour
{
    private void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("GoodCore") || other.CompareTag("BadCore"))
        {
            Debug.Log(other.gameObject.name + " with tag " + other.tag + " is being destroyed.");
            Destroy(other.gameObject);
        }
    }
}