# Import the libraries
import pickle
import csv
import mysql.connector
from mysql.connector import errorcode
import sys
import pandas as pd

# Set the paths to the files
path_to_website_data = 'G:/My Drive/Colab Notebooks/00 - Lambton/2022.1/04 - AML3406 - AI and ML Capstone Project/Player-Performance-Improvement-Prediction/Scripts/website_data.pkl'
path_to_csv_backup = 'G:/My Drive/Colab Notebooks/00 - Lambton/2022.1/04 - AML3406 - AI and ML Capstone Project/Player-Performance-Improvement-Prediction/Scripts/latest_data_sql.csv'

# This file is included in .gitignore
# It is a csv file with three columns.
# The headers are: user, password, and database
path_to_sql_settings = 'G:/My Drive/Colab Notebooks/00 - Lambton/2022.1/04 - AML3406 - AI and ML Capstone Project/Player-Performance-Improvement-Prediction/Scripts/sql_database_settings.csv'

# Boolean to set if there is a SQL database to be updated
connect_to_sql_database = False

# Load the data
try:
    with open(path_to_website_data, 'rb') as f:
        data = pickle.load(f)
except:
    print("Error loading the data")
    sys.exit()

if connect_to_sql_database:
    try:
        with open(path_to_sql_settings) as f:
            spamreader = csv.reader(f, delimiter=',')
            sql_settings = [row for row in spamreader]
            user = sql_settings[1][0]
            password = sql_settings[1][1]
            database = sql_settings[1][2]
    except:
        print("Error loading the SQL settings")
        sys.exit()

def connect_to_sql():
    try:
        connection = mysql.connector.connect(user=user,
                                            password=password,
                                            database=database)
        cursor = connection.cursor()
        return connection, cursor

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
          print(err)
    sys.exit()

def insert_values_sql(data):
    player_name = str(data[0])
    salary = float(data[1])
    team = str(data[2])
    position = str(data[3])
    draftking = float(data[4])

    try:
        QUERY = f'INSERT INTO sys.players(player_name, salary, team, position, draftking) VALUES("{player_name}", {salary}, "{team}", "{position}", {draftking})'
        cursor.execute(QUERY)
    except:
        print("Error inserting new values")
        connection.close()
        sys.exit()

def delete_all_values():
    QUERY = 'DELETE FROM sys.players'
    try:
        cursor.execute(QUERY)
    except:
        print("Error deleting the old data")
        connection.close()
        sys.exit()

if connect_to_sql_database:
    # Connect to the database
    connection, cursor = connect_to_sql()

    # Delete all values
    delete_all_values()

    # Insert the new values
    for value in data.values:
        insert_values_sql(value)

    try:
        connection.commit()
    except:
        print("Error commiting the changes")
        sys.exit()
    finally:
        connection.close()

# Save a csv file with the latest data
try:
    data.to_csv(path_to_csv_backup)
except:
    print('Error saving the csv backup')