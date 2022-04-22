import pickle
from tensorflow import keras
import sys

# Paths to the files
path_to_input_data = 'G:/My Drive/Colab Notebooks/00 - Lambton/2022.1/04 - AML3406 - AI and ML Capstone Project/Player-Performance-Improvement-Prediction/Scripts/filtered_model_input.pkl'
path_to_scaler = 'G:/My Drive/Colab Notebooks/00 - Lambton/2022.1/04 - AML3406 - AI and ML Capstone Project/Player-Performance-Improvement-Prediction/Models/Keras model/scaler.pkl'
path_to_model = 'G:/My Drive/Colab Notebooks/00 - Lambton/2022.1/04 - AML3406 - AI and ML Capstone Project/Player-Performance-Improvement-Prediction/Models/Keras model/model.h5'
path_to_predictions = 'G:/My Drive/Colab Notebooks/00 - Lambton/2022.1/04 - AML3406 - AI and ML Capstone Project/Player-Performance-Improvement-Prediction/Scripts/predictions.pkl'

# Load the input data
try:
    with open(path_to_input_data,'rb') as f:
        df = pickle.load(f)
except:
    print('Error loading the input data')
    sys.exit()

# Get the players' names from the input data
player_names = df['Player Name']

# Adjust the dataset to match the model requirements
columns_order = ['Minutes played', 'Field Goals Made',
              'Field Goals Attempted', 'Field Goals 3 Points Made',
              'Field Goal 3 Points Attempt', 'Free Throws Made',
              'Free Throws Attempt', 'Offensive Rebounds', 'Defensive Rebounds',
              'Assists', 'Steals', 'Blocks', 'Turnovers', 'Personal Fouls', 'Points',
              'Double-double', 'Triple-double']

df = df[columns_order]

# Get the data from the dataset
model_input = df.values

# Load the scalar used on the training data to scale the input data
try:
    with open(path_to_scaler,'rb') as f:
        scaler = pickle.load(f)
except:
    print('Error loading the scaler')
    sys.exit()

# Scale the data
model_input = scaler.transform(model_input)

# Load the model
try:
    model = keras.models.load_model(path_to_model)
except:
    print('Error loading the model')
    sys.exit()

# Get the predictions
predictions = model.predict(model_input)

# Dictionary with the players' names as keys and the predictions as values
model_output = {value.lower(): predictions[idx][0] for idx, value in enumerate(player_names)}

# Save the model output dictionary
try:
    with open(path_to_predictions, 'wb') as f:
        pickle.dump(model_output, f)
except:
    print('Error saving the model_output')