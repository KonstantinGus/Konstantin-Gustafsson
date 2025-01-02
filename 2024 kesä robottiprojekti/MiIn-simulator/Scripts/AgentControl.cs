using System.Collections.Generic;
using Unity.MLAgents.Actuators;
using Unity.MLAgents.Sensors;
using Unity.MLAgents;
using UnityEngine;
using System.Collections;

public class AgentControl : Agent
{
    public Transform OwnGoal;
    public Transform EnemyGoal;
    public GameObject badCorePrefab;
    public GameObject goodCorePrefab;
    public Transform[] goodCoreSpawnPoints;
    public Transform[] badCoreSpawnPoints;

    private Rigidbody agentRb;
    private float moveSpeed = 3f;
    private float rotateSpeed = 100f;
    private float spawnInterval = 30.0f;
    private float gameTime = 149.0f;
    private float timer = 0.0f;
    private int badCoreCount = 0;
    private bool gameEnded = false;
    private BoxCollider ownGoalCollider;
    private BoxCollider enemyGoalCollider;
    private List<GameObject> spawnedGoodCores = new List<GameObject>();
    private List<GameObject> spawnedBadCores = new List<GameObject>();

    public override void Initialize()
    {
        agentRb = GetComponent<Rigidbody>();
        ownGoalCollider = OwnGoal.GetComponent<BoxCollider>();
        enemyGoalCollider = EnemyGoal.GetComponent<BoxCollider>();
        StartCoroutine(SpawnBadCore());
    }

    public override void OnEpisodeBegin()
    {
        transform.localPosition = new Vector3(3.4f, 0.25f, 2.28f);
        transform.rotation = Quaternion.Euler(0, -135, 0);
        agentRb.velocity = Vector3.zero;
        agentRb.angularVelocity = Vector3.zero;

        foreach (GameObject badCore in GameObject.FindGameObjectsWithTag("BadCore"))
        {
            Destroy(badCore);
        }
        spawnedBadCores.Clear();

        foreach (GameObject goodCore in spawnedGoodCores)
        {
            Destroy(goodCore);
        }
        spawnedGoodCores.Clear();

        ResetGoodCores();
        badCoreCount = 0;
        timer = 0.0f;
        gameEnded = false;
    }

    public override void CollectObservations(VectorSensor sensor)
    {
        sensor.AddObservation(transform.localPosition); //Agent's Position 3 observations
        sensor.AddObservation(agentRb.velocity); //Agent's Velocity 3 observations

        sensor.AddObservation(OwnGoal.localPosition); //Own Goal Position 3 observations
        sensor.AddObservation(EnemyGoal.localPosition); //Enemy Goal Position 3 observations

        foreach (GameObject goodCore in spawnedGoodCores)
        {
            if (goodCore != null)
            {
                sensor.AddObservation(goodCore.transform.localPosition); //Positions of Good Cores 8*3 = 24 observations
            }
            else
            {
                sensor.AddObservation(Vector3.zero); 
            }
        }

        foreach (GameObject badCore in spawnedBadCores)
        {
            if (badCore != null)
            {
                sensor.AddObservation(badCore.transform.localPosition); //Positions of Bad Cores 4*3 = 12 observations
            }
            else
            {
                sensor.AddObservation(Vector3.zero);
            }
        }

        // Total = 48 observations
    }

    public override void OnActionReceived(ActionBuffers actions)
    {
        if (gameEnded) return;

        float moveRotate = actions.ContinuousActions[0];
        float moveForward = actions.ContinuousActions[1];

        // Moving the agent
        Vector3 moveDirection = transform.forward * moveForward * moveSpeed * Time.deltaTime;
        agentRb.MovePosition(transform.position + moveDirection);

        // Rotating the agent
        transform.Rotate(Vector3.up, moveRotate * rotateSpeed * Time.deltaTime);
    }

    public override void Heuristic(in ActionBuffers actionsOut)
    {
        ActionSegment<float> continuousActions = actionsOut.ContinuousActions;
        continuousActions[0] = Input.GetAxisRaw("Horizontal");
        continuousActions[1] = Input.GetAxisRaw("Vertical");
    }

    private void OnCollisionEnter(Collision collision)
    {
        if (collision.gameObject.CompareTag("GoodCore"))
        {
            if (IsInGoal(collision.gameObject.transform, ownGoalCollider))
            {
                Destroy(collision.gameObject);
                spawnedGoodCores.Remove(collision.gameObject);
                AddReward(15.0f);
            }
            else if (IsInGoal(collision.gameObject.transform, enemyGoalCollider))
            {
                Destroy(collision.gameObject);
                spawnedGoodCores.Remove(collision.gameObject);
                AddReward(-5.0f);
            }
            else
            {
                AddReward(0.1f);
            }
        }
        else if (collision.gameObject.CompareTag("BadCore"))
        {
            if (IsInGoal(collision.gameObject.transform, enemyGoalCollider))
            {
                Destroy(collision.gameObject);
                spawnedBadCores.Remove(collision.gameObject);
                AddReward(15.0f);
            }
            else if (IsInGoal(collision.gameObject.transform, ownGoalCollider))
            {
                Destroy(collision.gameObject);
                spawnedBadCores.Remove(collision.gameObject);
                AddReward(-5.0f);
            }
            else
            {
                AddReward(0.1f);
            }
        }
    }


    private bool IsInGoal(Transform obj, BoxCollider goalCollider)
    {
        Bounds bounds = goalCollider.bounds;
        Vector3 objPosition = obj.position;
        return bounds.Contains(objPosition);
    }

    private IEnumerator SpawnBadCore()
    {
        while (!gameEnded)
        {
            yield return new WaitForSeconds(spawnInterval);

            if (badCoreCount < badCoreSpawnPoints.Length)
            {
                Transform spawnPoint = badCoreSpawnPoints[badCoreCount];
                Vector3 spawnPosition = spawnPoint.position;

                GameObject newBadCore = Instantiate(badCorePrefab, spawnPosition, Quaternion.identity);

                Rigidbody badCoreRb = newBadCore.GetComponent<Rigidbody>();
                if (badCoreRb != null)
                {
                    badCoreRb.mass = 1.0f;
                }

                spawnedBadCores.Add(newBadCore);
                badCoreCount++;
            }
        }
    }

    private void ResetGoodCores()
    {
        for (int i = 0; i < goodCoreSpawnPoints.Length; i++)
        {
            GameObject goodCore = Instantiate(goodCorePrefab, goodCoreSpawnPoints[i].position, goodCoreSpawnPoints[i].rotation);
            spawnedGoodCores.Add(goodCore);
        }
    }

    private void ResetBadCores()
    {
        for (int i = 0; i < badCoreSpawnPoints.Length; i++)
        {
            GameObject badCore = Instantiate(badCorePrefab, badCoreSpawnPoints[i].position, badCoreSpawnPoints[i].rotation);
            spawnedBadCores.Add(badCore);
        }
    }

    private void Update()
    {
        if (gameEnded) return;

        timer += Time.deltaTime;

        if (timer >= gameTime)
        {
            gameEnded = true;
            EndEpisode();
        }
    }
}
