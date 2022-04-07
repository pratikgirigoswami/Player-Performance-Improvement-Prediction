# Import the libraries
import pandas as pd
import pickle
import time
import sys

from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.endpoints import leaguegamefinder

# Set the variables
season = '2021-22'
season_id = '22021'
season_type = 'Regular Season'
reference_path_game_by_game = 'G:/My Drive/Colab Notebooks/00 - Lambton/2022.1/04 - AML3406 - AI and ML Capstone Project/GitHub/Player-Performance-Improvement-Prediction/Scripts/game_by_game_dataset.pkl'
reference_path_mean_10_games = 'G:/My Drive/Colab Notebooks/00 - Lambton/2022.1/04 - AML3406 - AI and ML Capstone Project/GitHub/Player-Performance-Improvement-Prediction/Scripts/mean_10_games_dataset.pkl'
reference_path_model_input = 'G:/My Drive/Colab Notebooks/00 - Lambton/2022.1/04 - AML3406 - AI and ML Capstone Project/GitHub/Player-Performance-Improvement-Prediction/Scripts/model_input.pkl'

# Array to store error messages
errors = []

# Load the historical data - Game by game
try:
    with open(reference_path_game_by_game, 'rb') as f:
        game_by_game_df = pickle.load(f)
except:
    errors.append('Error loading the game by game historical data')

# Load the historical data - Mean last 10 games
try:
    with open(reference_path_mean_10_games, 'rb') as f:
        mean_10_games_df = pickle.load(f)
except:
    errors.append('Error loading the mean 10 games historical data')

# Stop the script execution in case of error loading the historical data
if len(errors) > 0:
    print(errors)
    sys.exit()

# Last date in the dataset
reference_date = mean_10_games_df['Game Date'].max()

# List of active players
try:
    active_players = players.get_active_players()
    players_ids = [str(player['id']) for player in active_players]
except:
    errors.append('Error loading the active players list')
    print(errors)
    sys.exit()

# Prepare the DataFrame to store the new data
columns = ['SEASON_ID', 'Player_ID', 'Game_ID', 'GAME_DATE', 'MATCHUP', 'WL',
    'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA',
    'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF',
    'PTS', 'PLUS_MINUS', 'VIDEO_AVAILABLE']

# DataFrame with the a new request (full season due api limitations)
latest_request = pd.DataFrame(columns=columns)

    # Request to get data from 'season'
for idx, id in enumerate(players_ids):
    print(f'Requesting data: {idx+1}/{len(players_ids)}', end='\r')
    try:
        data = playergamelog.PlayerGameLog(
            player_id=id,
            season=season,
            season_type_all_star=season_type,
            league_id_nullable='00',
            timeout=10)
    
        latest_request = pd.concat([latest_request, data.get_data_frames()[0]])
        
        # Preventing timeout exceptions
        time.sleep(.600)
    except:
        print(f'There was some problem while gathering data from player #{id}.')

if latest_request.shape[0] == 0:
    errors.append('There was a problem loading data with nba_api')
    print(errors)
    sys.exit()

# Adjust the Game Date type (to datetime)
latest_request['GAME_DATE'] =  pd.to_datetime(latest_request['GAME_DATE'])

# DataFrame with the new data
new_df = latest_request[latest_request['GAME_DATE'] > reference_date].copy()

if new_df.shape[0] == 0:
    errors.append('There is no new data')
    print(errors)
    sys.exit()

# Adjust the column names
new_column_names = ['Season ID', 'Player ID', 'Game ID', 'Game Date', 'Matchup', 'Won or Lost',
       'Minutes played', 'Field Goals Made', 'Field Goals Attempted', 'Field Goals %', 
       'Field Goals 3 Points Made', 'Field Goal 3 Points Attempt', 'Field Goal 3 Points %', 
       'Free Throws Made', 'Free Throws Attempt', 'Free Throw %', 'Offensive Rebounds', 'Defensive Rebounds', 'Rebounds', 
       'Assists', 'Steals', 'Blocks', 'Turnovers', 'Personal Fouls',
       'Points', 'Plus Minus', 'Video Available']
    
new_df.columns = new_column_names

# Drop irrelevant columns
columns_to_drop = ['Field Goals %', 'Field Goal 3 Points %', 
                'Free Throw %', 'Rebounds', 'Plus Minus', 'Video Available']

new_df.drop(columns=columns_to_drop, inplace=True, axis=1)

# Remove na
new_df.dropna(inplace=True)
new_df.reset_index(drop=True, inplace=True)

# Add Won or Lost feature
new_df['Won or Lost'].replace({'W': 1, 'L': 0}, inplace=True)
new_df.rename(columns={'Won or Lost': 'Won'}, inplace=True)

# Adjust the datatypes
columns_to_int = ['Minutes played', 'Field Goals Made', 'Field Goals Attempted',
       'Field Goals 3 Points Made', 'Field Goal 3 Points Attempt',
       'Free Throws Made', 'Free Throws Attempt', 'Offensive Rebounds',
       'Defensive Rebounds', 'Assists', 'Steals', 'Blocks', 'Turnovers',
       'Personal Fouls', 'Points']

columns_to_str = ['Season ID', 'Player ID', 'Game ID', 'Matchup']

new_df[columns_to_int] = new_df[columns_to_int].apply(pd.to_numeric)
new_df[columns_to_str] = new_df[columns_to_str].apply(lambda x: x.astype(str))

# Include the players' names
new_df['Player Name'] = new_df['Player ID'].apply(lambda x: str(active_players[players_ids.index(str(x))]['full_name']))

# Get players' teams
game_finder = leaguegamefinder.LeagueGameFinder(season_nullable=season, season_type_nullable=season_type)
games = game_finder.get_data_frames()[0]

def get_team_name(player_id, game_id):
    if new_df[(new_df['Player ID'] == player_id) & (new_df['Game ID'] == game_id)]['Won'].values[0]:
        return games[(games['GAME_ID'] == game_id) & (games['WL'] == 'W')]['TEAM_ABBREVIATION'].values[0]
    else:
        return games[(games['GAME_ID'] == game_id) & (games['WL'] == 'L')]['TEAM_ABBREVIATION'].values[0]

player_team = []
for idx, row in new_df.iterrows():
    player_team.append(get_team_name(row['Player ID'], row['Game ID']))

new_df['Player Team'] = player_team

# Get Home (1) x Away (0) info
new_df['Home'] = new_df['Matchup'].apply(lambda x: 0 if x[4] == '@' else 1)
new_df['Opponent'] = new_df['Matchup'].apply(lambda x: x[-3:])

new_columns_order = ['Season ID', 'Player ID', 'Player Name',
                    'Game ID', 'Game Date', 'Matchup', 'Player Team', 'Opponent', 'Home', 'Won',
                    'Minutes played', 'Field Goals Made', 'Field Goals Attempted',
                    'Field Goals 3 Points Made', 'Field Goal 3 Points Attempt',
                    'Free Throws Made', 'Free Throws Attempt', 'Offensive Rebounds',
                    'Defensive Rebounds', 'Assists', 'Steals', 'Blocks', 'Turnovers',
                    'Personal Fouls', 'Points']

new_df = new_df[new_columns_order]

# Include PER
pers = []
for idx, row in new_df.iterrows():
    if row['Minutes played'] == 0:
        per = 0
    else:
        per = round((row['Field Goals Made'] * 85.910 + row['Steals'] * 53.897 + row['Field Goals 3 Points Made'] * 51.757 + row['Free Throws Made'] * 46.845 + row['Blocks'] * 39.190 + row['Offensive Rebounds'] * 39.190 + row['Assists'] * 34.677 + row['Defensive Rebounds'] * 14.707 - row['Personal Fouls'] * 17.174 - (row['Free Throws Attempt'] - row['Free Throws Made']) * 20.091 - (row['Free Throws Attempt'] - row['Free Throws Made']) * 39.190 - row['Turnovers'] * 53.897) * (1 / row['Minutes played']), 3)
    pers.append(per)

new_df['Player Efficiency Ratings'] = pers

# Include double-double and triple-double
def get_double_and_triple_doubles(player_info):
    points = player_info['Points']
    rebounds = player_info['Offensive Rebounds'] + player_info['Defensive Rebounds']
    assists = player_info['Assists']
    blocks = player_info['Blocks']
    steals = player_info['Steals']

    stats = [points, rebounds, assists, blocks, steals]

    cnt = 0
    for stat in stats:
        if int(stat) >= 10:
            cnt += 1

    if cnt >= 3:
        return 'Triple-double'
    elif cnt == 2:
        return 'Double-double'
    else: 
        return None

new_df = new_df.reset_index(drop=True)
results = []

for index, row in new_df.iterrows():
    results.append(get_double_and_triple_doubles(row))

new_df['Double/Triple double'] = results

new_df['Double-double'] = new_df['Double/Triple double'].apply(lambda x: 1 if x == 'Double-double' else 0)
new_df['Triple-double'] = new_df['Double/Triple double'].apply(lambda x: 1 if x == 'Triple-double' else 0)

new_df.drop(['Double/Triple double'], axis=1, inplace=True)

# Get DraftKings score
def get_draftkings_score(player_info):
    points = player_info['Points']
    three_points = player_info['Field Goals 3 Points Made']
    rebounds = player_info['Offensive Rebounds'] + player_info['Defensive Rebounds']
    assists = player_info['Assists']
    steals = player_info['Steals']
    blocks = player_info['Blocks']
    turnovers = player_info['Turnovers']
    double_double = player_info['Double-double']
    triple_double = player_info['Triple-double']

    return points*1 + three_points*0.5 + rebounds*1.25 + assists*1.5 * steals*2 + blocks*2 + turnovers*(-0.5) + double_double*1.5 + triple_double*3

new_df = new_df.reset_index(drop=True)

results = []

for index, row in new_df.iterrows():
    results.append(get_draftkings_score(row))

new_df['DraftKings score'] = results

# Save the new Game by Game dataset
game_by_game_df.sort_values('Game Date', ascending=False).head(3)

game_by_game_df = pd.concat([game_by_game_df, new_df])
game_by_game_df.sort_values('Game Date', inplace=True)
game_by_game_df.reset_index(drop=True, inplace=True)

try:
    with open(reference_path_game_by_game, 'wb') as f:
        pickle.dump(game_by_game_df, f)
except:
    errors.append('Error saving the game by game data')
    print(errors)
    sys.exit()

# Prepare to update the mean 10 games dataset
def get_player_mean_stats(new_df, game_by_game_df, n_games):
    
    columns_to_drop = ['Season ID', 'Player ID', 'Player Name', 
                    'Game ID', 'Game Date', 'Matchup', 'Player Team', 
                    'Opponent', 'Home', 'Won', 'DraftKings score']
    
    players_ids = new_df['Player ID'].unique()

    mean_values = []
    game_dates = []
    season_ids = []
    player_ids_list = []
    player_names = []
    game_ids = []
    draftkings_scores = []
    
    for player_id in players_ids:
        number_of_new_rows = new_df[new_df['Player ID'] == player_id].shape[0]
        sub_df = game_by_game_df[game_by_game_df['Player ID'] == player_id].sort_values('Game Date', ascending=False).head(number_of_new_rows + n_games)
        sub_df = sub_df.sort_values('Game Date', ascending=True)
        sub_df.reset_index(drop=True, inplace=True)
        for index, row in sub_df.iterrows():
            if index + 1 > n_games:
                mean_values.append(sub_df.iloc[index+1-n_games : index+1].drop(columns_to_drop, axis=1).mean())
                game_dates.append(row['Game Date'])
                season_ids.append(row['Season ID'])
                player_ids_list.append(row['Player ID'])
                player_names.append(row['Player Name'])
                game_ids.append(row['Game ID'])
                draftkings_scores.append(row['DraftKings score'])
                                
    results_mean = pd.DataFrame(data=mean_values)
    results_mean['Game Date'] = game_dates
    results_mean['Season ID'] = season_ids
    results_mean['Player ID'] = player_ids_list
    results_mean['Player Name'] = player_names
    results_mean['Game ID'] = game_ids
    results_mean['Draftkings score'] = draftkings_scores    

    return results_mean

# Get the mean of the last 10 games for the new data
try:
    new_mean_10_games_df = get_player_mean_stats(new_df, game_by_game_df, 10)
except:
    errors.append('Error calculating the mean 10 games data')
    print(errors)
    sys.exit()

# Update the mean 10 games dataset (all historical values)
mean_10_games_df = pd.concat([mean_10_games_df, new_mean_10_games_df])
mean_10_games_df.sort_values('Game Date', inplace=True)
mean_10_games_df.reset_index(drop=True, inplace=True)

# Save the new dataset
try:
    with open(reference_path_mean_10_games, 'wb') as f:
        pickle.dump(mean_10_games_df, f)
except:
    errors.append('Error saving the mean 10 games data')
    print(errors)
    sys.exit()

# Prepare the new predictions dataset
players_latest_data = []
players_not_found = []
for id in players_ids:
    try: 
        players_latest_data.append(mean_10_games_df[(mean_10_games_df['Player ID'] == id) & (mean_10_games_df['Season ID'] == season_id)].sort_values('Game Date', ascending=False).iloc[0])
    except:
        players_not_found.append(id)

if len(players_not_found) > 0:
    print(f'Number of players not found: {len(players_not_found)}')

if len(players_latest_data) > 0:
    model_input = pd.DataFrame(players_latest_data)

    # Save a dataset with the new data (model input)
    try:
        with open(reference_path_model_input, 'wb') as f:
            pickle.dump(model_input, f)
    except:
        errors.append('Error saving the input data')
        print(errors)
        sys.exit()

else:
    print('No new data was added to the model input pickle file')