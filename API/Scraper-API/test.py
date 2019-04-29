import argparse
import requests
import re
import json
from bs4 import BeautifulSoup


# Create argument parser object.
parser = argparse.ArgumentParser(description='Process command line arguments')

# Create required args group header.
requiredArgs = parser.add_argument_group('required arguments')

# Call our object's add argument function.
requiredArgs.add_argument('-b','--bundleid', help='The bundle id of the app you wish to pull.', required=True)

# Store our argument input.
args = parser.parse_args()

url = "https://play.google.com/store/apps/details?id=" + args.bundleid
page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')


app = {}

# App name
app['name'] = soup.title.get_text().replace(' - Apps on Google Play', '')

# Cover art url
for img in soup.find_all('img'):
    if "Cover art" in str(img):
        app['cover art'] = img.get('src')
        break

# App description
for desc in soup.find_all('meta'):
    if 'itemprop="description"' in str(desc):
        app['description'] = desc.get('content')
        break

# App version
if len(soup.find_all(text=re.compile('Varies with device'))) > 0:
    app['version'] = 'Varies with device'
else:
    for span in soup.find_all('span'):
        if "htlgb" in str(span) and re.search('(?:(?:\d+|[a-z])[.-]){2,}(?:\d+|[a-z])', str(span)) and "div" not in str(span):
            app['version'] = span.contents[0]
            break

# App updated date
for dates in soup.find_all('span'):
    if re.search('(January|February|March|April|May|June|July|August|September|October|November|December)\s\d\d?,\s\d\d\d\d', str(dates)):
        app['updated'] = dates.span.contents[0]
        break

# Print JSON 
print(json.dumps(app, indent=1))


def main():
    pass

if __name__ == '__main__':
    main()