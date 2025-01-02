package com.example.teht5_konstantingustafsson

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView


class monthlyAdapter(private val dataSet: List<Day>) :
    RecyclerView.Adapter<monthlyAdapter.ViewHolder>() {

    /**
     * Provide a reference to the type of views that you are using
     * (custom ViewHolder)
     */
    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val textViewA: TextView
        val textViewA2: TextView

        init {
            // Define click listener for the ViewHolder's View
            textViewA = view.findViewById(R.id.textViewA)
            textViewA2 = view.findViewById(R.id.textViewA2)
        }
    }

    // Create new views (invoked by the layout manager)
    override fun onCreateViewHolder(viewGroup: ViewGroup, viewType: Int): ViewHolder {
        // Create a new view, which defines the UI of the list item
        val view = LayoutInflater.from(viewGroup.context)
            .inflate(R.layout.text_row_item, viewGroup, false)

        return ViewHolder(view)
    }

    // Replace the contents of a view (invoked by the layout manager)
    override fun onBindViewHolder(viewHolder: ViewHolder, position: Int) {

        // Get element from your dataset at this position and replace the
        // contents of the view with that element

        viewHolder.textViewA.text = dataSet[position].day.toString() + ". päivä:"

        viewHolder.textViewA2.text = dataSet[position].total.toString()
    }

    // Return the size of your dataset (invoked by the layout manager)
    override fun getItemCount() = dataSet.size

}

