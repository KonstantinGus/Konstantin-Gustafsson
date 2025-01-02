package com.example.teht3

import android.content.SharedPreferences
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import androidx.appcompat.app.AppCompatActivity
import androidx.preference.PreferenceFragmentCompat
import androidx.preference.PreferenceManager.getDefaultSharedPreferences

class SettingsActivity : AppCompatActivity() {


    lateinit var sharedPrefs:SharedPreferences



    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.settings_activity)

        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        sharedPrefs =getDefaultSharedPreferences(this)

        var alkuSaved = sharedPrefs.getFloat("alkuTaksa", 10f)
        var taksaSaved = sharedPrefs.getFloat("taksa", 10f)


        var taksaET = findViewById<EditText>(R.id.editTextTaksa)
        var alkuET = findViewById<EditText>(R.id.editTextAlku)
        taksaET.setText(taksaSaved.toString())
        alkuET.setText(alkuSaved.toString())



        findViewById<Button>(R.id.button3).setOnClickListener{
            var taksa = taksaET.text
            var alku = alkuET.text
            var taksaFloat = taksa.toString().toFloat()
            var alkuFloat = alku.toString().toFloat()
            with (sharedPrefs.edit()){
                putFloat("taksa", taksaFloat)
                putFloat("alkuTaksa", alkuFloat)
                apply()
            }
            finish()
        }

    }

    class SettingsFragment : PreferenceFragmentCompat() {
        override fun onCreatePreferences(savedInstanceState: Bundle?, rootKey: String?) {
            setPreferencesFromResource(R.xml.root_preferences, rootKey)
        }
    }
}