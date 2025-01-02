using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace Kalonator9000
{
    public class Meal
    {
        public string Name { get; set; }
        public int Energy { get; set; }
    }

    public class DailyFoodLog
    {
        public DateTime Pvm { get; set; }
        public List<Meal> DiaryMeals { get; set; }
    }

    public class Kuvaaja
    {
        public ObservableCollection<string> DateList { get; set; }
        public ObservableCollection<double> EnergySumList { get; set; }

        public Kuvaaja()
        {
            DateList = new ObservableCollection<string>();
            EnergySumList = new ObservableCollection<double>();
        }

        public void LoadJsonData(string jsonData)
        {
            // Avaa JSON datan to objekteihin
            var foodLogs = JsonConvert.DeserializeObject<DailyFoodLog[]>(jsonData);

            DateList.Clear();
            EnergySumList.Clear();

            foreach (var foodLog in foodLogs)
            {
                DateList.Add(foodLog.Pvm.ToString("yyyy-MM-dd"));
                EnergySumList.Add(foodLog.DiaryMeals.Sum(meal => meal.Energy));
            }
        }
    }
}