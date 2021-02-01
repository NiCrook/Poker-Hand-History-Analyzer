# IMPORT
import csv
import datetime
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
    password="LoTTaB0llyw00d"
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


def create_sql_database(cursor, db_name):
    try:
        cursor.execute(f"CREATE DATABASE {db_name} DEFAULT CHARACTER SET 'utf8'")
    except mysql.Error as err:
        print(f"Failed to create database: {err}\n")
        exit(1)


def insert_into_sql_table(cursor, sql_table, data):
    try:
        cursor.execute(f"INSERT INTO {sql_table} ({data}) VALUES (%s)")
    except mysql.Error as err:
        print(f"Failed to insert {data} into {sql_table}")


class HistoryDirectory:
    session_files = []

    def __init__(self, user_name):
        """
        A set of files that contain hand history data from the user
        :param user_name: Users ACR playername
        """
        self.user_name = user_name

    def find_profile_history(self):
        """
        Get file directory of user profile's hand history
        :return: Append each file to 'session_files'
        """
        profile_dir_str = "C:\\AmericasCardroom\\handHistory\\" + str(self.user_name)
        profile_dir = os.listdir(profile_dir_str)
        for file in profile_dir:
            HistoryDirectory.session_files.append((profile_dir_str + "\\" + file))


class FileRow:
    def __init__(self, file):
        """
        Get a specific row from a specific file
        :param file_name: Get file name to use
        :param row_no: Get row number to use
        """
        self.file = file

    def __str__(self):
        return str(self.__dict__)

    def check_row(self, string_check):
        if not self.file:
            pass
            # print("New hand...")
        else:
            if string_check in self.file[0]:
                return True
        """
        Check if selected string is in selected row of selected file
        :param string_check: String to check
        :return: Boolean
        """


class Session:
    def __init__(self, file):
        """
        Get session data per file
        :param file_name:
        """
        self.file = file
        self.table_name = ""
        self.date = ""
        self.hands = {}
        self.no_of_hands = int
        self.times_played = int
        self.results = int

    def __str__(self):
        return str(self.__dict__)

    def check_for_table_name(self):
        """
        Check for table name from first hand
        :return: self.table_name
        """
        self.table_name = self.file[1][0][:self.file[1][0].index(" ")]
        return self.table_name

    def check_date(self):
        """
        Check for date of first hand
        :return: self.date
        """
        self.date = self.file[0][0][-21:-13]
        return self.date

    def check_hands(self, ind):
        """
        Get hand number and hand start time, set into dict 'hands'
        Get number of hands played in session from getting length of self.hands dict
        :param ind: Current row number
        :return: self.hands, self.no_of_hands
        """
        self.hands[self.file[ind][0][self.file[ind][0].index("#") + 1:self.file[ind][0].index("-") - 1]] =\
            self.file[ind][0][-12:-4]
        self.no_of_hands = len(self.hands)
        return self.hands, self.no_of_hands

    def check_time_played(self):
        """
        Get first hand start time and last hand start time, find time difference between the two
        :return: total_time
        """
        time_start = datetime.datetime.strptime(list(self.hands.values())[0], '%H:%M:%S')
        end_time = datetime.datetime.strptime(list(self.hands.values())[-1], '%H:%M:%S')
        total_time = end_time - time_start
        return total_time


class Table:
    def __init__(self, table_name, table_stake, table_size, dates_played, times_played, hands_played, results):
        self.table_name = table_name
        self.table_stake = table_stake
        self.table_size = table_size
        self.dates_played = dates_played
        self.times_played = times_played
        self.hands_played = hands_played
        self.results = results


class Player:
    def __init__(self, player_name, sessions_played, hands_played, results):
        self.player_name = player_name
        self.sessions_played = sessions_played
        self.hands_played = hands_played
        self.results = results


class Hand:
    def __init__(self, hand_number, players, date, results):
        self.hand_number = hand_number
        self.players = players
        self.date = date
        self.results = results


if __name__ == '__main__':
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
    dir = HistoryDirectory("PolarFox")
    dir.find_profile_history()
    for file in range(0, len(dir.session_files)):
        session_file = open(dir.session_files[file], 'r')
        file_reader = list(csv.reader(session_file, delimiter="\n"))
        sess = Session(file_reader)
        print(sess.check_for_table_name())
        print(sess.check_date())
        # print(f"this is file_reader[0]: {file_reader[0]}")
        counter = 0
        while counter != len(file_reader):
            file = FileRow(file_reader[counter])
            if file.check_row("Hand #"):
                sess.check_hands(counter)
                counter += 1
            else:
                counter += 1
        print(sess.hands)
        print(sess.no_of_hands)
        print(sess.check_time_played())