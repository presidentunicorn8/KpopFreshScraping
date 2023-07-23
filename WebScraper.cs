using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using KpopFresh.Model;
using HtmlAgilityPack;
using System.Web;
using System.Net.Http.Json;
using System.Text.RegularExpressions;
using System.Globalization;
using System;
using System.Collections.Generic;
using System.IO;
using Newtonsoft.Json;


namespace KpopFresh.Services
{
    public class WebScraper
    {
        public async Task<string> getViewCount(string videoid)
        {
            string st = "";
            try
            {
                HttpClient client = new HttpClient();
                var apilink = "https://www.googleapis.com/youtube/v3/videos?part=statistics&id=" + videoid + "&key=AIzaSyAP7CPhoJDPwiOjBFllAhm_-VjAe1Ao5N8";

                // get the data from json
                var responseData = await client.GetByteArrayAsync(apilink); // success!
                UTF8Encoding utf8 = new UTF8Encoding();
                String Lyrics = utf8.GetString(responseData, 210, 60);
                // get just the numerical digits
                var number = Regex.Matches(Lyrics, @"\d+")
                      .Cast<Match>()
                      .Select(x => Convert.ToDouble(x.Value))
                      .ToList().First();
                // convert to stylish string
                
                if (number > 1000000)
                {
                    st = Math.Floor(number / 1000000).ToString() + "M views";
                }
                else if (number > 1000)
                {
                    st = Math.Floor(number / 1000).ToString() + "K views";
                }
                else
                {
                    st = number.ToString() + " views";
                }
            }
            catch
            {
                st = "0 views"; 
            }
            
            return st; 
        }

        public async Task<List<Song>> GetItems(DateOnly todayDate)
        {

            string thismonth = todayDate.ToString("MMMM-yyyy").ToLower();
            string thismo = DateTime.Now.ToString("MMMM").ToLower();
            int monthlength = thismo.Length;

            var html = @$"http://webcache.googleusercontent.com/search?q=cache:https://kpopofficial.com/kpop-comeback-schedule-{thismonth}/&strip=1&vwsrc=0";
            
            HtmlWeb web = new HtmlWeb();
            var htmlDoc = web.Load(html);

            // words to filter out
            List<string> badwords = new List<string>{
            "Twitter", "Music Video", "KPOP ARTISTS", "COMEBACK DATE", "Teaser", "KST", "Spotify Release", "Official Release", "Stage Video", "Official Audio", "release", "Release"
            };

            // Create a list of all other scrapable items
            List<string> unfilteredList = new List<string> { "FIRST" };
            foreach (HtmlNode n in htmlDoc.DocumentNode.SelectNodes("//tr/td"))
            {
                if (n.ChildNodes.Count > 0)
                {
                    foreach (HtmlNode j in n.ChildNodes)
                    {
                        if (!badwords.Any(word => Regex.IsMatch(j.InnerHtml, @$"\b{word}\b", RegexOptions.IgnoreCase))
                            && HttpUtility.HtmlDecode(j.InnerHtml) != unfilteredList.Last()
                            && HttpUtility.HtmlDecode(j.InnerHtml) != "")
                        {
                            // add the text item
                            unfilteredList.Add(HttpUtility.HtmlDecode(j.InnerHtml));
                            // the link sources
                            string hrefValue = j.Attributes["href"]?.Value ?? String.Empty;
                            if (hrefValue != "") { unfilteredList.Add(hrefValue); }
                        }
                    }

                }
            }
            // new list of objects
            List<Song> songList = new List<Song>();
            
            // For each new line in the list
            for (int i = 1; i < unfilteredList.Count; i++)
            {
                //if it's a date (new entry)
                if (unfilteredList[i].Contains(", 20"))
                {
                    int currPos = unfilteredList[i].IndexOf(", 20"); 
                    int endPos = unfilteredList[i].IndexOf(", 20") + 2;
                    int startPos = Math.Max(0, unfilteredList[i].IndexOf(", 20") - (monthlength + 2)); // find start position of datetime portion
                    // if it is a Two digit number data
                    if (char.IsDigit(unfilteredList[i][currPos - 2]))
                    {
                        startPos = unfilteredList[i].IndexOf(", 20") - (monthlength + 3); // find start position of datetime portion

                    }
                    string dateString = unfilteredList[i].Substring(startPos, endPos - startPos); // extract datetime portion as a string

                    try
                    {
                        DateTime.Parse(dateString); 
                    }
                    catch
                    {
                        dateString = $"{thismo} 30, 2023"; 
                    }

                    string thedate = dateString; 
                    string theartist = unfilteredList[i + 1];

                    // for all items from the first of description to the possible end
                    for (int j = i + 2; j < unfilteredList.Count; j++)
                    {
                        // if it isn't the link or the next date - the stop point
                        if (unfilteredList[j].Contains("https"))
                        {
                            string thelink = unfilteredList[j];
                            var videoid = thelink.Split('/').Last();
                            var theimage = $"https://img.youtube.com/vi/{videoid}/default.jpg";
                            // embed the view count in the description
                            var viewcount = ""; 
                            if (thelink.Contains("youtu.be/")) { viewcount = await getViewCount(videoid); }
                            var listsegment = unfilteredList.GetRange(i + 2, (j - 1) - (i + 2));
                            var desc = String.Join("\n", listsegment.ToArray());

                            i = j;
                            songList.Add(new Song(thedate, theartist, desc, theimage, thelink, viewcount));
                            break;
                        }
                        else if (unfilteredList[j].Contains(", 20"))
                        {
                            var listsegment = unfilteredList.GetRange(i + 2, (j - 1) - (i + 1));
                            var desc = String.Join("\n", listsegment.ToArray());
                            var thelink = "no";
                            var theimage = "white.png";
                            var viewcount = ""; 

                            i = j;
                            songList.Add(new Song(thedate, theartist, desc, theimage, thelink, viewcount));
                            break;
                        }
                    }
                }
            }
            //songList.Add(new Song("", "", "", "white.png", "no")); // debug empty element

            return songList;
        }
    }
}
