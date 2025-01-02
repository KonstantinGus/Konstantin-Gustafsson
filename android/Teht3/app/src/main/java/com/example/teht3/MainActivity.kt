package com.example.teht3

import android.content.Intent
import android.content.SharedPreferences
import android.media.RouteListingPreference.Item
import android.os.Bundle
import com.google.android.material.snackbar.Snackbar
import androidx.appcompat.app.AppCompatActivity
import androidx.navigation.findNavController
import androidx.navigation.ui.AppBarConfiguration
import androidx.navigation.ui.navigateUp
import androidx.navigation.ui.setupActionBarWithNavController
import android.view.Menu
import android.view.MenuItem
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.preference.PreferenceManager.getDefaultSharedPreferences
import com.example.teht3.databinding.ActivityMainBinding
import org.w3c.dom.Text

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    lateinit var sharedPrefs: SharedPreferences



    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setSupportActionBar(binding.toolbar)

        sharedPrefs = getDefaultSharedPreferences(this)


        binding.fab.setImageResource(R.drawable.add_circle)


        binding.fab.setOnClickListener {
            var kilometritTeksti = findViewById<EditText>(R.id.editNumber).text
            var tulosTeksti = findViewById<TextView>(R.id.textView)
            var taksa = sharedPrefs.getFloat("taksa", 10f)
            var alkuTaksa = sharedPrefs.getFloat("alkuTaksa", 10f)
            var kmString = kilometritTeksti.toString()
            var km = kmString.toFloat()
            var tulos = taksa * km
            tulos += alkuTaksa
            tulosTeksti.setText(tulos.toString() + "€")
        }


    }


    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        // Inflate the menu; this adds items to the action bar if it is present.
        menuInflater.inflate(R.menu.menu_main, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        return when (item.itemId) {
            R.id.action_settings ->
            {
                val settingsItent = Intent(this, SettingsActivity::class.java)
                //startForResult.launch(settingsItent)
                startActivity(settingsItent)
                true
            }
            else -> super.onOptionsItemSelected(item)
        }
    }


}