using System.Text;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
using LiveCharts;
using LiveCharts.Wpf;
using System;
using System.IO;
using LiveCharts.Definitions.Charts;
using Newtonsoft.Json;
using System.Windows.Threading;



namespace Kalonator9000
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        public Kuvaaja ViewModel { get; set; }

        public void UpdateData(string jsonData)
        {
            ViewModel = new Kuvaaja();
            DataContext = ViewModel;

            var foodLogs = JsonConvert.DeserializeObject<DailyFoodLog[]>(jsonData);
            ViewModel.LoadJsonData(jsonData);


            Labels = new List<string>(ViewModel.DateList);
            YFormatter = value => value.ToString();

            SeriesCollection.Clear();
            SeriesCollection.Add(new LineSeries
            {
                Title = "Kcal/päivä:",
                Values = new ChartValues<double>(ViewModel.EnergySumList),
                LineSmoothness = 0.2,
                PointGeometry = DefaultGeometries.Diamond,
                PointGeometrySize = 15,
                PointForeground = Brushes.Khaki
            });

            DataContext = this;
        }

        public MainWindow()
        {
            InitializeComponent();
            {
                SeriesCollection = new SeriesCollection();
                {

                }
            }

            Loaded += MainWindow_Loaded;

            ViewModel = new Kuvaaja();
            DataContext = ViewModel;


            string jsonFilePath = @"..\\..\\..\\pvkirja.json";
            string jsonData = File.ReadAllText(jsonFilePath);

            // Lataa initial JSON datan
            ViewModel.LoadJsonData(jsonData);


            Labels = new List<string>(ViewModel.DateList);
            YFormatter = value => value.ToString();

            //series collectionin modaaminen päivittää chartin

            SeriesCollection.Add(new LineSeries
            {
                Title = "Kcal/päivä:",
                Values = new ChartValues<double>(ViewModel.EnergySumList),
                LineSmoothness = 0.2, // 0 = suoria linjoja, 1 = sileä ku Esa
                PointGeometry = DefaultGeometries.Diamond, //Minkä näköne piste chartilla
                PointGeometrySize = 15, //minkä kokosta
                PointForeground = Brushes.Khaki //En tiiä tekeekö mitään
            });

            //Series arvojen päivittäminen myös animoi ja päivittää chartin

            DataContext = this;
        }

        private void MainWindow_Loaded(object sender, RoutedEventArgs e)
        {
            var values = new ChartValues<double>();

            var r = new Random();
            for (var i = 0; i < 100; i++)
            {
                values.Add(r.Next(0, 10));
            }

            cartesianChart1.AxisX.Add(new Axis
            {
                MinValue = 0,
                MaxValue = Labels.Count,
            });
        }

        public SeriesCollection SeriesCollection { get; set; }
        public List<string> Labels { get; set; }
        public Func<double, string> YFormatter { get; set; }




        private void Window_MouseDown(object sender, MouseButtonEventArgs e)
        {
            if (e.LeftButton == MouseButtonState.Pressed)
                DragMove();
        }
        private void btnMinimize_Click(object sender, RoutedEventArgs e)
        {
            WindowState = WindowState.Minimized;
        }

        private void Button_Click(object sender, RoutedEventArgs e) // Laskurin avaus tähän
        {
            Laskuri winLaskuri = new Laskuri();
            DispatcherTimer timer = new DispatcherTimer();
            timer.Interval = TimeSpan.FromSeconds(1);
            timer.Tick += (s, args) =>
            {
                this.Hide();
                timer.Stop();
            };
            timer.Start();
            winLaskuri.Show();
        }

        private void btnClose_Click(object sender, RoutedEventArgs e)
        {
            Application.Current.Shutdown();
        }

        private void paivakirjaButton_Click(object sender, RoutedEventArgs e) //Päiväkirjan avaus
        {
            paivakirja winPaivakirja = new paivakirja();

            DispatcherTimer timer = new DispatcherTimer();
            timer.Interval = TimeSpan.FromSeconds(1);
            timer.Tick += (s, args) =>
            {
                this.Hide();
                timer.Stop();
            };
            timer.Start();
            winPaivakirja.Show();
        }

        //Scrollaus
        private void Taaksepäin_Click(object sender, RoutedEventArgs e)
        {
            cartesianChart1.AxisX[0].MinValue -= 10;
            cartesianChart1.AxisX[0].MaxValue -= 10;
        }

        private void Eteenpäin_Click(object sender, RoutedEventArgs e)
        {
            cartesianChart1.AxisX[0].MinValue += 10;
            cartesianChart1.AxisX[0].MaxValue += 10;
        }

        //Zooming
        private void Zoom_Click(object sender, RoutedEventArgs e)
        {
            cartesianChart1.AxisX[0].MinValue = 5;
            cartesianChart1.AxisX[0].MaxValue = 10;
        }

        private void Unzoom_Click(object sender, RoutedEventArgs e)
        {
            cartesianChart1.AxisX[0].MinValue = 0;
            cartesianChart1.AxisX[0].MaxValue = Labels.Count;
        }
    }
}