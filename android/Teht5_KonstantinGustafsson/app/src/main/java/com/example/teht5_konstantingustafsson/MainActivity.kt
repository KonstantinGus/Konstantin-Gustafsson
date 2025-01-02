package com.example.teht5_konstantingustafsson

import android.content.Intent
import android.os.Bundle
import android.widget.Adapter
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.GET

interface Service {
    @GET("api/data/year")
    fun callCall ( ): Call<Year>
}


class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        val textView = findViewById<TextView>(R.id.textView)

        val retrofit = Retrofit.Builder()
            .baseUrl("https://korkeasaarenkavijat.onrender.com")
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        val service = retrofit.create(Service::class.java)
        val yearYear = service.callCall()

        val recycler = findViewById<RecyclerView>(R.id.recyclerView)
        recycler.layoutManager = LinearLayoutManager(this)



        yearYear?.enqueue(object : Callback<Year> {
            override fun onResponse(call: Call<Year>, response: Response<Year>) {
                if (response.code() == 200) {

                    val yearResponse = response.body()!!
                    var mAdapter = MyAdapter(yearResponse.months)
                    recycler.adapter = mAdapter
                    textView.text = "Korkeasaaren kävijät kuukausittain\n"
                    textView.text = textView.text.toString() + "Vuonna " + yearResponse.year.toString() +"\n"
                    /*for (x:Month in yearResponse.months){
                        //var mAdapter = MyAdapter(x)
                        textView.text = textView.text.toString() + monthNames[x.month]+"kuu" + " " +  x.total.toString() +"\n"

                    }
                    textView.text = textView.text.toString() + "Yhteensä: " + yearResponse.total.toString() + " kävijää"*/



                }
            }



            override fun onFailure(call: Call<Year>, t: Throwable) {
                textView.text = t.message
            }
        })
    findViewById<Button>(R.id.button).setOnClickListener(){
        val intent = Intent(this, TammikuuActivity::class.java)
        startActivity(intent)
    }
}}