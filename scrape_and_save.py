from bs4 import BeautifulSoup
import requests
import json
import datetime
import math
import googleapiclient.discovery

def get_first_video_id(search_term):
  """Gets the first video ID for a given search term.

  Args:
    search_term: The search term to use.
    api_key: The YouTube Data API key.

  Returns:
    The video ID of the first result, or None if no results were found.
  """

  youtube = googleapiclient.discovery.build("youtube", "v3", developerKey="AIzaSyAP7CPhoJDPwiOjBFllAhm_-VjAe1Ao5N8")

  request = youtube.search().list(
      part="snippet",
      maxResults=1,
      q=search_term,
      type="video"
  )
  response = request.execute()

  if not response['items']:
    return None

  return response['items'][0]['id']['videoId']

def getViewCount(videoid):
    st = ""

    try:
        apilink = "https://www.googleapis.com/youtube/v3/videos?part=statistics&id=" + videoid + "&key=AIzaSyAP7CPhoJDPwiOjBFllAhm_-VjAe1Ao5N8"
        # get the data from json
        response = requests.get(apilink)
    except:
        st = "0 views"
        return st

    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        try:
            # Get the 'viewCount' from the JSON response
            number = int(data['items'][0]['statistics']['viewCount'])
        except: 
            return "0 views"

        if number > 1000000:
            st = str(math.floor(number / 1000000)) + "M views"
        elif number > 1000:
            st = str(math.floor(number / 1000)) + "K views"
        else:
            st = str(number) + " views"
        
    else:
        st = "0 views"

    return st
#datetime current date
def getData(current_date):
    month_name = current_date.strftime("%B").lower()
    year = current_date.strftime("%Y")
    
    url = f"https://kpopofficial.com/kpop-comeback-schedule-{month_name}-{year}/"
    response = requests.get(url)
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    
    
    badwords = ["SCHEDULE", "ALLKPOP", "SONG CATEGORIES", "NAVIGATION", "ANY KOREAN SONGS", "UPDATED EVERYDAY", "TWITTER", "NEWS", "KPOP ARTISTS", "COMEBACK DATE", "TEASER", "KST", "SPOTIFY", "STAGE VIDEO", "AUDIO", "RELEASE"]
    badwordsforlater = ["MUSIC VIDEO", "OFFICIAL", "YOUTUBE", "LYRICS"]
    # Find all <tr> tags followed by <td> tags using the BeautifulSoup find_all method
    # This will give you a list of all <td> elements inside <tr> elements
    td_elements = soup.find_all('td')  # You can use 'td' instead of 'tr' to find direct <td> elements
    
    unfilteredList = ['first']
    # populate unfilteredList
    for n in td_elements:
        for child in n.children:
            if ((not any(word in child.text.upper() for word in badwords))
               and child.text != unfilteredList[-1]
               and child.text != ""):
                unfilteredList.append(child.text)
    
                if child.name == 'a' and 'href' in child.attrs:
                    if child['href'] != '':
                        unfilteredList.append(child['href'])
    
    # new list of objects
    songList = []
    date_format = "%B %d, %Y"
    
    for i, element in enumerate(unfilteredList):
        if ", 20" in element:
            # Remove the colon from the date string
            cleaned_date_string = element.split(":")[0].lstrip()
            try:
                # Convert the cleaned date string to a DateTime object
                date_object = datetime.datetime.strptime(cleaned_date_string, "%B %d, %Y")
                thedate = cleaned_date_string
            except:
                thedate = f"{month_name.capitalize()} 28, 2023"
            desc = ""
            theartist = unfilteredList[i+1]
            if month_name.capitalize() in theartist:
                continue
    
            # instantiate default values
            thelink = "no"
            theimage = "white.png"
            viewcount = ""; 
            for x in unfilteredList[int(i)+2: len(unfilteredList)]:
                if ", 20" in x:
                    break
                elif "https" in x:
                    thelink = x
                    
                    # embed the view count in the description
                    if "youtu.be/" in thelink:
                        # get last element from link as videoid
                        splitlink = thelink.split('/')
                        videoid = splitlink[-1]
                        # get rid of extra information from links
                        if '&' in videoid:
                            videoid2 = videoid.split('&')
                            videoid = videoid2[0]
                        if '?' in videoid:
                            videoid2 = videoid.split('?')
                            videoid = videoid2[0]
                            
                        theimage = f"https://img.youtube.com/vi/{videoid}/default.jpg"
                        viewcount = getViewCount(videoid)
                else:
                    if not any(word in x.upper() for word in badwordsforlater):
                        if desc == "":
                            desc = x
                        else:
                            desc += "\n" + x
            if thelink == "no":
                try:
                    datetime_object = datetime.datetime.strptime(thedate, "%B %d, %Y")
                    if datetime_object < datetime.datetime.now()-datetime.timedelta(days=2):
                        videoid = get_first_video_id(theartist + " " + x)
                        if videoid:
                            theimage = f"https://img.youtube.com/vi/{videoid}/default.jpg"
                            viewcount = getViewCount(videoid)
                            thelink = f"youtu.be/{videoid}"
                except:
                    pass
    
            mydict = dict(Name = thedate, Artist = theartist, 
                        Details = str(desc), ImageUrl = theimage,
                        SongLink= thelink, ViewCount = viewcount)
            songList.append(mydict) 
    return songList

# Get the current date
current_date = datetime.datetime.now()
# Calculate the first day of the current month
first_day_of_current_month = current_date.replace(day=1)
# Subtract one day from the first day of the current month to get the last day of the last month
last_date = first_day_of_current_month - datetime.timedelta(days=1)
# Calculate the first day of the next month by adding one month to the first day of the current month
next_date = (first_day_of_current_month + datetime.timedelta(days=32)).replace(day=1)

for x in [last_date, current_date, next_date]:
    songList = getData(x)
    if len(songList) == 0:
        mydict = dict(Name = x.strftime("%B").lower(), Artist = "No data yet", 
                        Details = "No data yet", ImageUrl = "white.png",
                        SongLink= "", ViewCount = "")
        songList.append(mydict) 
    month_as_string = str(x.month)
    file_title = f"data-{month_as_string}.json"
    # Export the list of dictionaries as JSON to a file
    with open(file_title, "w", encoding="utf-8") as json_file:
        json.dump(songList, json_file, indent=4, ensure_ascii=False)
