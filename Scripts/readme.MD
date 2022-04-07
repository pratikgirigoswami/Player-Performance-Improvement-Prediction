# Summary of the scripts' order of execution and description 

## 0_get_new_data.py
Get new data and update the pickle datasets (game by game and mean 10 games)

## 1_get_injured_players.py
Get data from the injured report

## 2_remove_from_injury_report.py
Remove the injuried players from the input data

## 3_get_predictions.py
Run the model and get the predictions

## 4_get_salary_and_position.py
Get salary, position and team data from DraftKings score

## 5_merge_data.py
Merge the output of the model with the salary and position

## 6_update_sql.py
It reads the pickle datasets and update the SQL tables