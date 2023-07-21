from urllib.request import urlopen
import json
import datetime

# Get the current date
current_date = datetime.datetime.now()
month_name = current_date.strftime("%B").lower()
year = current_date.strftime("%Y")

url = f"https://kpopofficial.com/kpop-comeback-schedule-{month_name}-{year}/"
page = urlopen(url)
html_bytes = page.read()
html = html_bytes.decode("utf-8")

# Save the HTML to a JSON file
timestamp = datetime.datetime.now().isoformat()
data = {"timestamp": timestamp, "html": html}

with open("output.json", "w") as json_file:
    json.dump(data, json_file, ensure_ascii=False, indent=4)
