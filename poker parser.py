# IMPORT
import csv
from datetime import datetime
import mysql.connector as mysql
from mysql.connector import errorcode
import os

"""
EXAMPLE HAND:"

Hand #576909116 - Omaha(No Limit) - $0.01/$0.02 - 2020/11/06 21:14:59 UTC
Powhattan 6-max Seat #1 is the button
Seat 1: PolarFox ($2.11)
Seat 2: Kattitude ($2.16)
Seat 3: ragu_sauce ($1.77)
Seat 4: FlopSavvy ($0.56)
Seat 6: IveysAFraud ($4.04)
Kattitude posts the small blind $0.01
ragu_sauce posts the big blind $0.02
*** HOLE CARDS ***
Dealt to PolarFox [Qh 3c Kd Ad]
FlopSavvy folds
IveysAFraud folds
PolarFox raises $0.07 to $0.07
Kattitude calls $0.06
ragu_sauce calls $0.05
*** FLOP *** [Kh 8c 6d]
Main pot $0.20 | Rake $0.01
Kattitude checks
ragu_sauce checks
PolarFox bets $0.12
Kattitude calls $0.12
ragu_sauce calls $0.12
*** TURN *** [Kh 8c 6d] [As]
Main pot $0.55 | Rake $0.02
Kattitude checks
ragu_sauce checks
PolarFox bets $0.19
Kattitude raises $1.97 to $1.97 and is all-in
ragu_sauce calls $1.58 and is all-in
PolarFox calls $1.73 and is all-in
Uncalled bet ($0.05) returned to Kattitude
*** RIVER *** [Kh 8c 6d As] [4h]
Main pot $5.05 | Rake $0.26
Side pot(1) $0.65 | Rake $0.03
*** SHOW DOWN ***
Main pot $5.05 | Rake $0.26
Side pot(1) $0.65 | Rake $0.03
PolarFox shows [Qh 3c Kd Ad] (two pair, Aces and Kings [As Ad Kh Kd 8c])
Kattitude shows [Tc Jc Ac Qc] (a pair of Aces [As Ac Kh Qc 8c])
ragu_sauce shows [2c 6h 6s 7c] (three of a kind, Set of Sixs [6s 6h 6d As Kh])
ragu_sauce collected $5.05 from main pot
PolarFox collected $0.65 from side pot-1
*** SUMMARY ***
Total pot $5.70 | Rake $0.21 | JP Fee $0.08
Board [Kh 8c 6d As 4h]
Seat 1: PolarFox (button) showed [Qh 3c Kd Ad] and won $0.65 with two pair, Aces and Kings [As Ad Kh Kd 8c]
Seat 2: Kattitude (small blind) showed [Tc Jc Ac Qc] and lost with a pair of Aces [As Ac Kh Qc 8c]
Seat 3: ragu_sauce (big blind) showed [2c 6h 6s 7c] and won $5.05 with three of a kind, Set of Sixes [6s 6h 6d As Kh]
Seat 4: FlopSavvy folded on the Pre-Flop and did not bet
Seat 6: IveysAFraud folded on the Pre-Flop and did not bet

"
"""

"""
Design function that returns the csv document or to store it as a variable?
SESSION -> TABLE -> HAND -> PLAYERS for tables
"""

sql_connection = mysql.connect(
    host="localhost",
    user="root",
    password="password"
)
cursor = sql_connection.cursor(buffered=True)

HAND_HISTORY_DB_NAME = 'Hand_History'
HAND_HISTORY_DB_TABLES = {}
HAND_HISTORY_DB_TABLES['Tables'] = (
    "CREATE TABLE `Tables` ("
    "   `Table Name` varchar(36),"
    "   `Table Date` date NOT NULL"
    ") ENGINE=InnoDB")
HAND_HISTORY_DB_TABLES['Hands'] = (
    "CREATE TABLE `Hands` ("
    "   `Hand Number` int(9),"
    "   `Hand Date` date NOT NULL"
    ") ENGINE=InnoDB")
HAND_HISTORY_DB_TABLES['Players'] = (
    "CREATE TABLE `Players` ("
    "   `Player` varchar(16),"
    "   `Hands Played` int(9)"
    ") ENGINE=InnoDB")

HAND_HISTORY_DIR = r"C:\AmericasCardroom\handHistory\PolarFox\\"
SESSIONS_DIR = os.listdir(HAND_HISTORY_DIR)
SESSION_FILES = []
SESSIONS = {}
for file in SESSIONS_DIR:
    SESSION_FILES.append(file)


def create_sql_database(cursor, db_name):
    try:
        cursor.execute(f"CREATE DATABASE {db_name} DEFAULT CHARACTER SET 'utf8'")
    except mysql.Error as err:
        print(f"Failed to create database: {err}\n")
        exit(1)


def check_row(file_row, string_check):
    if string_check in str(file_row):
        return True


def session_file_reader(file):
    index = 0
    hand_count = 0
    player_count = 0
    hand_start_times = []
    hand_numbers = []
    player_names = []
    player_seats = []
    blinds_posted = {}

    session_file = open(HAND_HISTORY_DIR + file, 'r')
    file_reader = list(csv.reader(session_file, delimiter="\n"))

    game_type = str(file_reader[0])[str(file_reader[0]).index("-") + 2:str(file_reader[0]).index("(")]
    limit_type = str(file_reader[0])[str(file_reader[0]).index("(") + 1:str(file_reader[0]).index(")")]
    limit_size = str(file_reader[0])[str(file_reader[0]).index("$"):
                                     str(file_reader[0]).index(" ", str(file_reader[0]).index("$"))]

    table_name = str(file_reader[1])[2:str(file_reader[1]).index(" ")]
    table_size = str(file_reader[1])[str(file_reader[1]).index(" ") + 1:
                                     str(file_reader[1]).index(" ", str(file_reader[1]).index(" ") + 1)]

    while index != len(file_reader):
        if check_row(file_reader[index], "Hand #"):
            hand_numbers.append(str(file_reader[index])[str(file_reader[index]).index("#") + 1:
                                                        str(file_reader[index]).index("-") - 1])
            hand_start_times.append(str(file_reader[index])[str(file_reader[index]).index(":") - 13:
                                                            str(file_reader[index]).index("U") - 1])
            hand_count += 1
        if check_row(file_reader[index], "is the button"):
            button_position = str(file_reader[index])[str(file_reader[index]).index("#") + 1]
        if check_row(file_reader[index], "Seat "):
            if check_row(file_reader[index], "($"):
                player_names.append(str(file_reader[index])[str(file_reader[index]).index(":") + 2:
                                                            str(file_reader[index]).index("(") - 1])
                player_seats.append(str(file_reader[index])[7])
        if check_row(file_reader[index], "the small blind"):
            blinds_posted["Small Blind"] = str(file_reader[index])[2:str(file_reader[index]).index(" ")]
        if check_row(file_reader[index], "the big blind"):
            blinds_posted["Big Blind"] = str(file_reader[index])[2:str(file_reader[index]).index(" ")]
        if check_row(file_reader[index], "posts $"):
            blinds_posted["Extra Blind"] = str(file_reader[index])[2:str(file_reader[index]).index(" ")]
        if check_row(file_reader[index], "posts dead"):
            blinds_posted["Dead Blind"] = str(file_reader[index])[2:str(file_reader[index]).index(" ")]
        index += 1
    return table_name, limit_size, table_size, hand_start_times[0], hand_start_times[
        -1], hand_count, player_names, player_seats, blinds_posted


try:
    cursor.execute(f"USE {HAND_HISTORY_DB_NAME}")
except mysql.Error as err:
    print(f"Database {HAND_HISTORY_DB_NAME} does not exist.")
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_sql_database(cursor, HAND_HISTORY_DB_NAME)
        print(f"Database {HAND_HISTORY_DB_NAME} created successfully.")
        sql_connection.database = HAND_HISTORY_DB_NAME
    else:
        print(err)
        exit(1)

for table_name in HAND_HISTORY_DB_TABLES:
    table_description = HAND_HISTORY_DB_TABLES[table_name]
    try:
        print(f"Creating table: {table_name}")
        cursor.execute(table_description)
        print(f"Created table: {table_name} successfully")
    except mysql.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print(f"Table {table_name} already exists.")
        else:
            print(err.msg)
cursor.execute("SHOW TABLES")
sql_connection.commit()
sql_connection.close()
cursor.close()


print(session_file_reader(SESSIONS_DIR[0]))
