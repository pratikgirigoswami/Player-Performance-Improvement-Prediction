# Import the libraries
import pickle
import sys

# Paths to the files
path_to_predictions = 'G:/My Drive/Colab Notebooks/00 - Lambton/2022.1/04 - AML3406 - AI and ML Capstone Project/GitHub/Player-Performance-Improvement-Prediction/Scripts/predictions.pkl'
path_to_salaries_and_positions = 'G:/My Drive/Colab Notebooks/00 - Lambton/2022.1/04 - AML3406 - AI and ML Capstone Project/GitHub/Player-Performance-Improvement-Prediction/Scripts/salaries_and_positions.pkl'
path_to_website_data = 'G:/My Drive/Colab Notebooks/00 - Lambton/2022.1/04 - AML3406 - AI and ML Capstone Project/GitHub/Player-Performance-Improvement-Prediction/Scripts/website_data.pkl'

# Load the predictions
try:
    with open(path_to_predictions, 'rb') as f:
        predictions = pickle.load(f)
except:
    print('Error loading the predictions')
    sys.exit()

# Load the players' salaries, positions and teams
try:
    with open(path_to_salaries_and_positions, 'rb') as f:
        salaries_and_positions = pickle.load(f)
except:
    print('Error loading the salary and positions DataFrame')
    sys.exit()

# List to store the common data between the two datasets
predictions_column = []
for player in salaries_and_positions['Name']:
    if player.lower() in list(predictions.keys()):
        predictions_column.append(predictions[player.lower()])
    else:
        predictions_column.append(None)

if len(predictions_column) == 0:
    print('No common data between the predictions dictionary and the salary_and_positions DataFrame')
    sys.exit()

# Include the data into the salaries_and_positions DataFrame and dropping the lines with missing values
salaries_and_positions['DraftKing Score'] = predictions_column
salaries_and_positions.dropna(inplace=True)

# Renaming the columns to match the SQL database
salaries_and_positions.columns = ['player_name', 'salary', 'team', 'position', 'draftking_score']

# Save the final data
try:
    with open(path_to_website_data, 'wb') as f:
        pickle.dump(salaries_and_positions, f)
except:
    print('Error saving the final DataFrame')