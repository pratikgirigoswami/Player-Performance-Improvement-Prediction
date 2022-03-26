import requests
import pandas as pd

# URL from DraftKing to download the csv file with all the salary and position data
csv_url = 'https://www.draftkings.com/lineup/getavailableplayerscsv?contestTypeId=70&draftGroupId=65997'
r = requests.get(csv_url, allow_redirects=True)

with open('Scripts/salaries_and_positions.csv', 'wb') as f:
    f.write(r.content)

df = pd.read_csv('Scripts/salaries_and_positions.csv')

columns_to_drop = ['Position', 'Name + ID', 'ID', 'Game Info', 'AvgPointsPerGame']
df.drop(columns=columns_to_drop, inplace=True)

# Rename the columns acording to the SQL table
df.columns = ['full_name', 'position', 'salary', 'team']

positions = [pos.split('/') for pos in df['position']]
df['position'] = positions

df.to_csv('Scripts/salaries_and_positions.csv', index=False)