import csv
import mysql.connector
from mysql.connector import errorcode

def connect_to_sql(user, password, database):
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


def insert_values_sql(data):
    id = data[0]
    full_name = data[1]
    team = data[2]
    salary = data[3]
    position = data[4]
    draftking = data[5]

    QUERY = f'INSERT INTO sys.players(id, full_name, team, salary, position, draftking) VALUES({id}, "{full_name}", "{team}", {salary}, "{position}", {draftking})'

    connection, cursor = connect_to_sql('root', 'admin', 'sys')
    cursor.execute(QUERY)

    connection.commit()
    connection.close()


def backup_sql_table():
    QUERY = 'SELECT * FROM sys.players'

    connection, cursor = connect_to_sql('root', 'admin', 'sys')
    
    cursor.execute(QUERY)
    
    with open(PATH_BACKUP, 'w', newline='') as f:
        spamwriter = csv.writer(f, delimiter=',')
        spamwriter.writerow(['id', 'full_name', 'team', 'salary', 'position', 'draftking'])
        for data_entry in cursor:
            spamwriter.writerow(list(data_entry))

    connection.close()


def drop_table():
    connection, cursor = connect_to_sql('root', 'admin', 'sys')
    QUERY = 'DELETE FROM sys.players'

    cursor.execute(QUERY)
    connection.commit()
    connection.close()    


if __name__ == '__main__':
    PATH_NEW_DATA = 'G:/My Drive/Colab Notebooks/00 - Lambton/2022.1/04 - AML3406 - AI and ML Capstone Project/GitHub/Player-Performance-Improvement-Prediction/Scripts/players.csv'
    PATH_BACKUP = 'G:/My Drive/Colab Notebooks/00 - Lambton/2022.1/04 - AML3406 - AI and ML Capstone Project/GitHub/Player-Performance-Improvement-Prediction/Scripts/backup_players.csv'

    # Reading the csv file
    with open(PATH_NEW_DATA) as f:
        spamreader = csv.reader(f, delimiter=',')
        data = [row for row in spamreader]

    # Removing the header
    data = data[1:]

    backup_sql_table()
    drop_table()

    for dt in data:
        insert_values_sql(dt)