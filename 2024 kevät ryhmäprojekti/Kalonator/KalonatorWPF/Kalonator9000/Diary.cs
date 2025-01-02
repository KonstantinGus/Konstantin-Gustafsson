using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;


namespace Kalonator9000
{
    class Diary
    {
        internal class DiaryEntries
        {
            public DateTime Pvm { get; set; }
            public List<DiaryMeals> DiaryMeals { get; set; }
        }
        internal class DiaryMeals
        {
            public string Name { get; set; }
            public int Energy { get; set; }
        }

        
    }
}
