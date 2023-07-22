from bs4 import BeautifulSoup
import requests
import json
import datetime
import math

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
        # Get the 'viewCount' from the JSON response
        number = int(data['items'][0]['statistics']['viewCount'])

        if number > 1000000:
            st = str(math.floor(number / 1000000)) + "M views"
        elif number > 1000:
            st = str(math.floor(number / 1000)) + "K views"
        else:
            st = number.ToString() + " views"
        
    else:
        st = "0 views"

    return st


# Get the current date
current_date = datetime.datetime.now()
month_name = current_date.strftime("%B").lower()
year = current_date.strftime("%Y")

url = f"https://kpopofficial.com/kpop-comeback-schedule-{month_name}-{year}/"
response = requests.get(url)
# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')



badwords = ["SCHEDULE", "ALLKPOP", "SONG CATEGORIES", "OFFICIAL YOUTUBE", "NAVIGATION", "ANY KOREAN SONGS", "UPDATED EVERYDAY", "TWITTER", "NEWS", "MUSIC VIDEO", "KPOP ARTISTS", "COMEBACK DATE", "TEASER", "KST", "SPOTIFY", "OFFICIAL", "STAGE VIDEO", "AUDIO", "RELEASE"]

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
        thedate = element
        desc = []
        theartist = unfilteredList[i+1]

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
                    theimage = f"https://img.youtube.com/vi/{videoid}/default.jpg"
                    viewcount = getViewCount(videoid)
            else:
                desc.append(x)

        mydict = dict(Name = thedate, Artist = theartist, 
                    Details = str(desc), ImageUrl = theimage,
                    SongLink= thelink, ViewCount = viewcount)
        songList.append(mydict)                    


# Export the list of dictionaries as JSON to a file
with open("data.json", "w", encoding="utf-8") as json_file:
    json.dump(songList, json_file, indent=4, ensure_ascii=False)
