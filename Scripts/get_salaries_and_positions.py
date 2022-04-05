# Import the libraries
import requests
import pandas as pd
import sys
import io
import pickle

path_to_file = 'G:/My Drive/Colab Notebooks/00 - Lambton/2022.1/04 - AML3406 - AI and ML Capstone Project/GitHub/Player-Performance-Improvement-Prediction/Scripts/salaries_and_positions.pkl'

# URL from DraftKing to download the csv file with all the salary and position data
try:
    csv_url = 'https://www.draftkings.com/lineup/getavailableplayerscsv?contestTypeId=70&draftGroupId=65997'
    r = requests.get(csv_url, allow_redirects=True)
except:
    print('There was an error loading the data from DraftKings website')
    sys.exit()

try:
    df = pd.read_csv(io.StringIO(r.content.decode('utf-8')))
    df = df[['Name', 'Roster Position', 'Salary', 'TeamAbbrev']]
except:
    print('There was an error reading the data from DraftKings.com')
    sys.exit()

positions = [pos.split('/') for pos in df['Roster Position']]
df['position'] = positions

df.drop(['Roster Position'], axis=1, inplace=True)

try:
    with open(path_to_file, 'wb') as f:
        pickle.dump(df, f)
except:
    print('There was an error saving the salaries and positions file')