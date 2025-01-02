package com.example.t2_konstantingustafsson
import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.util.AttributeSet
import android.view.View


class Point(val X:Float, val Y:Float)


class MyView(context: Context?, attrs: AttributeSet?) : View(context, attrs) {
    val paint = Paint()
    var x1 = 50f
    var y1 = 50f
    var pisteet = listOf<Point>()

    override fun onDraw (canvas: Canvas){
        super.onDraw(canvas)
        paint.color = Color.RED
        canvas.drawCircle(x1, y1 , 50.0f, paint)
        paint.color = Color.BLACK
        for (p in pisteet){
            canvas.drawCircle(p.X, p.Y, 10f, paint)
        }
    }

    fun setXY (X: Float, Y: Float): Unit{
        x1 = X
        y1 = Y
        pisteet = pisteet.plus(Point(X, Y))
        invalidate()
    }

}

