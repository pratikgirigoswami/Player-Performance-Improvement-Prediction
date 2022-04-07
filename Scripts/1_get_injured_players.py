# Import the libraries
import requests
import pickle
from bs4 import BeautifulSoup
import sys

reference_path_injury_report = 'G:/My Drive/Colab Notebooks/00 - Lambton/2022.1/04 - AML3406 - AI and ML Capstone Project/GitHub/Player-Performance-Improvement-Prediction/Scripts/injury_report.pkl'

# Get the data from the espn website
url = 'https://www.espn.com/nba/injuries'

try:
    page = requests.get(url)
except:
    print('Error requesting data from espn.com/nba/injuries')
    sys.exit()

soup = BeautifulSoup(page.content, 'html.parser')
table = soup.find_all(class_="AnchorLink")

rows = []
content = [list(entry.contents)[0] for entry in table if len(list(entry.contents)[0]) > 0]

start = False
players = []
for line in content:
    if start:
        if str(line)[0] == '<':
            break
        players.append(line)
    if list(line)[0] == "Fantasy Men's Basketball":
        start = True

if len(players) == 0:
    print('Error: No player in the injury report')
    sys.exit()

# Pickle doesnt handle well lists
players = ', '.join(players)

# Save the pickle file with the injury report
try:
    with open(reference_path_injury_report, 'wb') as f:
        pickle.dump(players, f)
except:
    print('Error saving the injury report')
