using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Text.Encodings.Web;
using System.Text.Json;
using System.Text.Unicode;
using System.IO;
using System.Reflection.Metadata;

namespace Kalonator9000
{
    class Ruoka_aineidenLatausJaTallennus
    {
        internal class JsonLatausTallennus
        {
            private const string TIEDOSTO_NIMI = "Ruokaaineet.json";
            
            private static string GetJSONpolku()
            {
                string polku = System.Reflection.Assembly.GetExecutingAssembly().Location;
                polku = Path.GetDirectoryName(polku);
                return Path.Combine(polku, TIEDOSTO_NIMI);
            }
            public static void Tallenna_aineet(List<Ruoka_aineLista> kivet)
            {
                try
                {
                    string oikeePolku = GetJSONpolku();
                    var JSONkivet = JsonSerializer.Serialize(kivet);
                    File.WriteAllText(oikeePolku, JSONkivet);
                }
                catch (Exception ex) { Console.WriteLine(ex); }

            }
            public static List<Ruoka_aineLista> Lataa_aineet()
            {
                try
                {
                    string polku = GetJSONpolku();
                    string raakaJSON = File.ReadAllText(polku);

                    var options3 = new JsonSerializerOptions
                    {
                        Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping,
                        WriteIndented = true
                    };

                    string puhdistettuJSON = JsonSerializer.Serialize(raakaJSON, options3);

                    var kivilista = JsonSerializer.Deserialize<List<Ruoka_aineLista>>(raakaJSON);
                    if (kivilista == null || kivilista.Count == 0) { return new List<Ruoka_aineLista>(); }
                    return kivilista;
                }
                catch (Exception ex) { Console.WriteLine(ex); }
                return new List<Ruoka_aineLista>();
            }
        }
    }
}
