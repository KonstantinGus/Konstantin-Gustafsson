using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Media.Media3D;

namespace Kalonator9000
{
    internal class DiaryEntries
    {
        public DateTime Pvm { get; set; }
        public List<DiaryMeals> DiaryMeals { get; set; }
    }
}
