# Import the library
import pickle
import sys
import pandas as pd

# Path to the Pickle files
path_model_input = 'G:/My Drive/Colab Notebooks/00 - Lambton/2022.1/04 - AML3406 - AI and ML Capstone Project/GitHub/Player-Performance-Improvement-Prediction/Scripts/model_input.pkl'
path_filtered_input = 'G:/My Drive/Colab Notebooks/00 - Lambton/2022.1/04 - AML3406 - AI and ML Capstone Project/GitHub/Player-Performance-Improvement-Prediction/Scripts/filtered_model_input.pkl'
path_injury_report = 'G:/My Drive/Colab Notebooks/00 - Lambton/2022.1/04 - AML3406 - AI and ML Capstone Project/GitHub/Player-Performance-Improvement-Prediction/Scripts/injury_report.pkl'

# Load the data
try:
    with open(path_model_input, 'rb') as f:
        model_input = pickle.load(f)

    with open(path_injury_report, 'rb') as f:
        injury_report = pickle.load(f)
except:
    print('There was an error loading the data')
    sys.exit()

# Adjust injury report format
injury_report = injury_report.split(', ')
injury_report = [name.lower() for name in injury_report]

# Lower the names for comparison
model_input['Name lower'] = model_input['Player Name'].apply(lambda x: x.lower())

# Create a column to indicate if the player is injuried 
model_input['Injury'] = model_input['Name lower'].apply(lambda x: 1 if x in injury_report else 0)

# DataFrame with only non injuried players
new_model_input = model_input[model_input['Injury'] == 0].copy()

if new_model_input.shape[0] == 0:
    print('Error! No players in the model_input file!')
    sys.exit()

# Drop the auxiliaries columns
new_model_input.drop(['Name lower', 'Injury'], axis=1, inplace=True)

# Keep only the more recent data
players_id = new_model_input['Player ID'].unique()

data = []
for id in players_id:
    data.append(new_model_input[new_model_input['Player ID'] == id].sort_values('Game Date', ascending=False).iloc[0])

recent_data = pd.DataFrame(data)

# Save the filtered data
try:
    with open(path_filtered_input, 'wb') as f:
        pickle.dump(recent_data, f)
except:
    print('Error saving the model_input file.')