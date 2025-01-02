using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Kalonator9000
{
    class Ruoka_aineLista
    {
        public double Energia { get; set; }
        public double Annos { get; set; }
        public string Nimi { get; set; }
        public Ruoka_aineLista(string Nimi, double Energia, double Annos)
        {
            this.Nimi = Nimi;
            this.Energia = Energia;
            this.Annos = Annos;
        }
    }
}
