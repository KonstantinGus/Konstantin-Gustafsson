using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.WebSockets;
using System.Text;
using System.Text.Json;

using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Shapes;

namespace Kalonator9000
{
    /// <summary>
    /// Interaction logic for paivakirja.xaml
    /// </summary>
    public partial class paivakirja : Window
    {


        public paivakirja()
        {
            InitializeComponent();
            List<Diary.DiaryEntries> entries = JsonSerializer.Deserialize<List<Diary.DiaryEntries>>(File.ReadAllText("..\\..\\..\\pvkirja.json"));
            entries.Reverse();
            foreach (Diary.DiaryEntries e1 in entries)
            {
                int tempsum = 0;

                foreach (var m1 in e1.DiaryMeals)
                {
                    tempsum += m1.Energy;
                }
                TreeViewItem x = new TreeViewItem();
                x.Header = e1.Pvm.ToShortDateString() +" - "+ tempsum.ToString() + " kcal";

                foreach (var m1 in e1.DiaryMeals)
                {
                TreeViewItem y = new TreeViewItem();
                    y.Header = m1.Name + ": " + m1.Energy + " kcal";
                    x.Items.Add(y);
                }
                DiaryView.Items.Add(x);

            }
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
    }
}
