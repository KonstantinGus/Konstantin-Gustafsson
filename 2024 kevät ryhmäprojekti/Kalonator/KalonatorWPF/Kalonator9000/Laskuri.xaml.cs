using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using static Kalonator9000.Ruoka_aineidenLatausJaTallennus;
using System.Text.Json;
using System.IO;


namespace Kalonator9000
{
    /// <summary>
    /// Interaction logic for Laskuri.xaml
    /// </summary>
    public partial class Laskuri : Window
    {
        List<Ruoka_aineLista> LaskurinRuokaLista = new List<Ruoka_aineLista>();
        List<Ruoka_aineLista> RuokaKirjasto = new List<Ruoka_aineLista>();
        public int Valittu = 0;

        public Laskuri()
        {
            InitializeComponent();

            RuokaKirjasto = JsonLatausTallennus.Lataa_aineet();
            RuokaKirjasto = RuokaKirjasto.OrderBy(Ruoka_aineLista => Ruoka_aineLista.Nimi).ToList();

            Label1.Content = "Valitse Ruoka yllä olevasta pudotusvalikosta.\nVoi kestää hetki Kun pudotusvalikko ensimmäisen kerran latautuu.";
            for (int i = 0; i<RuokaKirjasto.Count; i++)
            {
                DropDown.Items.Add(RuokaKirjasto[i].Nimi);
            };
        }

        private void DropDown_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            ComboBox cmb = (ComboBox)sender;
            int VanhaValittu = Valittu;
            Valittu = cmb.SelectedIndex;
            if (Valittu != -1)
            {
                Label1.Content =
                "Nimi: " + RuokaKirjasto[Valittu].Nimi
              + "\nKalorit (kCal/100g): " + RuokaKirjasto[Valittu].Energia
              + "\nAnnoskoko (g): " + RuokaKirjasto[Valittu].Annos;
            } else { Valittu = VanhaValittu; }
        }

        private void LisääRuokaan(object sender, RoutedEventArgs e)
        {
            LisääLaskuriin(RuokaKirjasto[Valittu].Annos);
        }

        public void LisääLaskuriin(double _Annos)
        {
            if (LaskurinRuokaLista.Any(n => n.Nimi == RuokaKirjasto[Valittu].Nimi))
            {
                int index = LaskurinRuokaLista.FindIndex(n => n.Nimi == RuokaKirjasto[Valittu].Nimi);
                LaskurinRuokaLista[index].Annos += RuokaKirjasto[Valittu].Annos;
                
            } 
            else
            {
                LaskurinRuokaLista.Add(new(RuokaKirjasto[Valittu].Nimi, RuokaKirjasto[Valittu].Energia, _Annos));
            };
            LaskurinRuokaaineLista.Content = LaskurinTeksti();
        }

        private void TyhjennäLista(object sender, RoutedEventArgs e)
        {
            LaskurinRuokaLista.Clear();
            LaskurinRuokaaineLista.Content = LaskurinTeksti();
        }

        public string LaskurinTeksti()
        {
            string _Teksti = "";

            double KaloritYht = 0;
            for (int i = 0; i < LaskurinRuokaLista.Count; i++)
            {
                KaloritYht += LaskurinRuokaLista[i].Energia*LaskurinRuokaLista[i].Annos/100;
            };
            KaloritYht = Math.Ceiling(KaloritYht * 100) / 100;
            _Teksti += "Kalorit yhteensä: " + KaloritYht + "\n";

            for (int i = 0; i < LaskurinRuokaLista.Count; i++)
            {
                _Teksti +=
                    LaskurinRuokaLista[i].Nimi + ":\n"
                  + "Kalorit (kCal/100g): " + LaskurinRuokaLista[i].Energia
                  + " Annoskoko (g): " + LaskurinRuokaLista[i].Annos + "\n";
                //if ((i+1)%2 == 0) { _Teksti += "\n"; } else { _Teksti += " | "; }
            };

            return _Teksti;
        }
        private void btnMinimize_Click(object sender, RoutedEventArgs e)
        {
            WindowState = WindowState.Minimized;
        }
        private void Window_MouseDown(object sender, MouseButtonEventArgs e)
        {
            if (e.LeftButton == MouseButtonState.Pressed)
                DragMove();
        }
        private void btnClose_Click(object sender, RoutedEventArgs e)
        {
            foreach (Window window in Application.Current.Windows)
            {
                if (window.GetType() == typeof(MainWindow))
                {
                    window.Show();
                }
            }
            Close();
        }

        private void LisääRuokaAine(object sender, RoutedEventArgs e)
        {
            bool PääseeLäpi = true;
            string nimi = UusiAineNimi.Text;
            string kalorit = UusiAineKalorit.Text;
            string annos = UusiAineAnnos.Text;

            double TuplaKalorit = 0;
            double TuplaAnnos = 0;

            try
            {
                TuplaKalorit = double.Parse(kalorit);
                if (TuplaKalorit < 0)
                {
                    UusiAineKalorit.Text = "Arvon tulee olla positiivinen luku.";
                    PääseeLäpi = false;
                };
            }
            catch
            {
                UusiAineKalorit.Text = "Arvossa voi olla vain numeroita.";
                PääseeLäpi = false;
            };

            try
            {
                TuplaAnnos = double.Parse(annos);
                if (TuplaAnnos < 0)
                {
                    UusiAineAnnos.Text = "Arvon tulee olla positiivinen luku.";
                    PääseeLäpi = false;
                };
            }
            catch
            {
                UusiAineAnnos.Text = "Arvossa voi olla vain numeroita.";
                PääseeLäpi = false;
            };

            if (nimi.Length == 0)
            {
                UusiAineNimi.Text = "Nimen tulee olla vähintään yhden kirjaimen pituinen.";
                PääseeLäpi = false;
            };

            if(PääseeLäpi)
            {
                DropDown.Items.Add(nimi);
                RuokaKirjasto.Add(new(nimi, TuplaKalorit, TuplaAnnos));

                UusiAineAnnos.Text = "";
                UusiAineNimi.Text = "";
                UusiAineKalorit.Text = "";
                
                JsonLatausTallennus.Tallenna_aineet(RuokaKirjasto);
            };
        }

        private void TallennaPäiväkirjaan(object sender, RoutedEventArgs e)
        {
            InitializeComponent();
            if(LaskurinRuokaLista.Count > 0)
            {
                List<Diary.DiaryEntries> entries = JsonSerializer.Deserialize<List<Diary.DiaryEntries>>(File.ReadAllText("..\\..\\..\\pvkirja.json"));

                //var tempentry1 = new Diary.DiaryEntries();
                
                var tempdate2 = entries[entries.Count - 1].Pvm;
                tempdate2 = tempdate2.Date;
                if (tempdate2 != DateTime.Now.Date)
                {
                    var tempentry1 = new Diary.DiaryEntries();
                    var date1 = DateTime.Now;
                    tempentry1.Pvm = date1;
                    tempentry1.DiaryMeals = [];
                    foreach (var e1 in LaskurinRuokaLista)
                    {
                        var tempmeal1 = new Diary.DiaryMeals();
                        tempmeal1.Name = e1.Nimi;
                        int tempenergia = Convert.ToInt32(Math.Ceiling(e1.Energia * (e1.Annos / 100)));
                        tempmeal1.Energy = tempenergia;
                        tempentry1.DiaryMeals.Add(tempmeal1);
                    }
                    entries.Add(tempentry1);
                }
                else
                {
                    var tempentry1 = entries[entries.Count - 1];
                    foreach (var e1 in LaskurinRuokaLista)
                    {
                        var tempmeal1 = new Diary.DiaryMeals();
                        tempmeal1.Name = e1.Nimi;
                        int tempenergia = Convert.ToInt32(Math.Ceiling(e1.Energia * (e1.Annos / 100)));
                        tempmeal1.Energy = tempenergia;
                        tempentry1.DiaryMeals.Add(tempmeal1);
                    }
                    entries[entries.Count - 1] = tempentry1;
                }
                
               



                

                File.WriteAllText("..\\..\\..\\pvkirja.json", JsonSerializer.Serialize(entries));

                LaskurinRuokaLista.Clear();
                LaskurinRuokaaineLista.Content = "Ruuat tallenettu päiväkirjaan.";

                //Updeittaa kuvaajan
                if (Application.Current.MainWindow is MainWindow mainWindow)
                {
                    string jsonFilePath = @"..\\..\\..\\pvkirja.json";
                    string jsonData = File.ReadAllText(jsonFilePath);

                    mainWindow.UpdateData(jsonData);
                }
            }

            
        }

        private void TarkkaAnnos(object sender, RoutedEventArgs e)
        {
            string annos = TarkkaAnnosKenttä.Text;
            double TuplaAnnos = 0;
            bool PääseeLäpi = true;
            try
            {
                TuplaAnnos = double.Parse(annos);
                if (TuplaAnnos < 0)
                {
                    TarkkaAnnosKenttä.Text = "Arvon tulee olla positiivinen luku.";
                    PääseeLäpi = false;
                };
            }
            catch
            {
                TarkkaAnnosKenttä.Text = "Arvossa voi olla vain numeroita.";
                PääseeLäpi = false;
            };

            if (PääseeLäpi)
            {
                LisääLaskuriin(TuplaAnnos);
                TarkkaAnnosKenttä.Text = "";
            }
        }

        private void UusiAineAnnos_TextChanged(object sender, TextChangedEventArgs e)
        {

        }
    }
}