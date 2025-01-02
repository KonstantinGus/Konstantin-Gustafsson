package com.example.teht5_konstantingustafsson

import android.os.Bundle
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

interface Service2 {

    @GET("api/data/month/0")
    fun getJanuaryVisitors(): Call<Month>
}

class TammikuuActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.tammikuu_activity)

        val textView2 = findViewById<TextView>(R.id.textView2)
        textView2.text = "Tammikuun kävijät:"


        val retrofit = Retrofit.Builder()
            .baseUrl("https://korkeasaarenkavijat.onrender.com")
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        val recycler = findViewById<RecyclerView>(R.id.recyclerViewJan)
        recycler.layoutManager = LinearLayoutManager(this)

        val service = retrofit.create(Service2::class.java)
        val januaryCall = service.getJanuaryVisitors()

        januaryCall.enqueue(object : Callback<Month> {
            override fun onResponse(call: Call<Month>, response: Response<Month>) {
                if (response.isSuccessful) {
                    val januaryVisitors = response.body()!!



                    var janAdapter = monthlyAdapter(januaryVisitors.days)
                    recycler.adapter = janAdapter



                } else {
                    textView2.text = response.message().toString()
                }
            }


            override fun onFailure(call: Call<Month>, t: Throwable) {
                textView2.text = t.message
            }
        })

    }
}
