package com.example.t2_konstantingustafsson

import android.os.Bundle
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager




class MainActivity : AppCompatActivity(), SensorEventListener  {

    private lateinit var sensorManager: SensorManager
    private var mLight: Sensor? = null
    private lateinit var myView: MyView




    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_main)



        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main)) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom)
            insets
        }
        sensorManager = getSystemService(SENSOR_SERVICE) as SensorManager
        mLight = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)

        myView = findViewById<MyView>(R.id.myView)




    }



    override fun onSensorChanged(event: SensorEvent){
        var x2 = 150f
        var y2 = 150f

        var temp0 = event.values[0]
        var temp1 = event.values[1]
        var temp2 = event.values[2]
        temp0 = temp0.toFloat()
        temp2 = temp2.toFloat()

        val factor = 100

        x2 = temp0 * factor
        y2 = temp2 * factor

        myView.setXY(x2, y2)


        //0 ja 2 suunta, 1 periaatteessa nopeus

    }



    override fun onAccuracyChanged(p0: Sensor?, p1: Int) {
        // Do something here if sensor accuracy changes.
    }


    override fun onResume() {
        super.onResume()
        sensorManager.registerListener(this, mLight, SensorManager.SENSOR_DELAY_NORMAL)
    }
    override fun onPause() {
        super.onPause()
        sensorManager.unregisterListener(this)
    }
}