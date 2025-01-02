package com.example.t1b_konstantingustafsson


import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.Spacer

import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.Button
import androidx.compose.material3.Checkbox
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.example.t1b_konstantingustafsson.ui.theme.T1b_KonstantinGustafssonTheme
import kotlin.math.pow
import kotlin.reflect.typeOf

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            T1b_KonstantinGustafssonTheme {
                Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
                    Greeting(
                        name = "Android",
                        modifier = Modifier.padding(innerPadding)
                    )
                }
            }
        }
    }
}

fun LaskeBmi(pituus :Double, paino : Double, aikuisuus: Boolean): Double {
    //var bmi = (0.13 * a) / (b.pow(2.5))
    var temp1 = pituus * 0.01
    temp1 = temp1.pow(2.5)
    var temp2 = paino * 1.3
    var bmi = temp2 / temp1
    if (aikuisuus) {return bmi}
    else{
        return 0.0
    }
}

@Composable
fun Greeting(name: String, modifier: Modifier = Modifier) {
    var pituus by remember { mutableStateOf("") }
    var paino by remember { mutableStateOf("") }
    var tulos by remember { mutableStateOf("Tähän tulee bmi") }
    var adulthood by remember { mutableStateOf(false) }
    Column {
        Spacer(modifier.padding(8.dp, 24.dp))
        Text(
            text = "BMI-laskuri",
            modifier = Modifier.padding(1.dp)
        )

        TextField(

            value = pituus,
            onValueChange = { pituus = it},
            label = {Text("Pituus (cm)")},
            keyboardOptions = KeyboardOptions.Default.copy(
                keyboardType = KeyboardType.Number
            )


        )

        TextField(
            value = paino,
            onValueChange = { paino = it},
            label = {Text("Paino (kg)")},
            keyboardOptions = KeyboardOptions.Default.copy(
                keyboardType = KeyboardType.Number
            )


        )
        Row {Checkbox(
            checked = adulthood,
            onCheckedChange = { adulthood = it
            }


        )
        Text("Oletko aikuinen?")}



    Button(onClick = {
        var bmiTulos = LaskeBmi(pituus = pituus.toDouble(), paino= paino.toDouble(), aikuisuus = adulthood)
        if (adulthood){tulos = bmiTulos.toString()}
        else {tulos = "virhe, ei lapsilla ole bmi:tä"}
    } ) {
        Text(
            text = "Laske"
        )
    }
        Text(
            text = tulos,
            modifier = Modifier.padding(1.dp)
        )
}}






@Preview(showBackground = true)
@Composable
fun GreetingPreview() {
    T1b_KonstantinGustafssonTheme {
        Greeting("Android")
    }
}