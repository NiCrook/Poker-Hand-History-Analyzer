# IMPORT
import csv
import datetime
from getpass import getpass
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
SESSION - TABLE - HAND - PLAYERS for tables
"""

sql_connection = mysql.connect(
    host="localhost",
    user="root",
    password="password"
)
cursor = sql_connection.cursor(buffered=True)

HAND_HISTORY_DB_NAME = 'HandHistory'
HAND_HISTORY_DB_TABLES = {}
HAND_HISTORY_DB_TABLES['Sessions'] = (
    "CREATE TABLE `Sessions` ("
    "   `SessionTable` varchar(36),"
    "   `SessionDate` date NOT NULL,"
    "   `SessionTime` time NOT NULL,"
    "   `SessionHands` int(6),"
    "   `SessionResults` float(16)"
    ")  ENGINE=InnoDB")
HAND_HISTORY_DB_TABLES['Tables'] = (
    "CREATE TABLE `PokerTables` ("
    "   `TableName` varchar(36),"
    "   `TableStake` varchar(16),"
    "   `TableSize` int(1),"
    "   `TableDate` date NOT NULL"
    ") ENGINE=InnoDB")
HAND_HISTORY_DB_TABLES['Hands'] = (
    "CREATE TABLE `Hands` ("
    "   `HandNumber` int(9),"
    "   `HandDate` date NOT NULL,"
    "   `HandResults` float(16)"
    ") ENGINE=InnoDB")
HAND_HISTORY_DB_TABLES['Players'] = (
    "CREATE TABLE `Players` ("
    "   `PlayerName` varchar(16)"
    # "   `PlayerSessions` int(6),"
    # "   `PlayerHands` int(9),"
    # "   `PlayerResults` float(16)"
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
        :return: Boolean
        """
        self.file = file

    def __str__(self):
        return str(self.__dict__)

    def check_row(self, string_check):
        if not self.file:
            pass
        else:
            if string_check in self.file[0]:
                return True


class Session:
    def __init__(self, file):
        """
        Get session data per file
        :param file_name:
        """
        self.file = file
        self.table_name = self.check_for_table_name
        self.table_stake = self.check_for_table_stake
        self.table_size = self.check_for_table_size
        self.date = self.check_date
        self.session_time = self.check_time_played
        self.hand_no = str
        self.hand_start = str
        self.hands = {}
        self.no_of_hands = int
        self.hand_results = []

        self.small = 0
        self.big = 0
        self.call_bet = 0
        self.bet_return = 0
        self._raise = 0 - self.bet_return
        self.won = 0
        self.actions = 0
        self.result = 0
        # self.session_results = self.hand_results[-1] - self.hand_results[0]

    def __str__(self):
        return str(self.__dict__)

    def check_for_table_name(self):
        """
        Check for table name from first hand
        :return: self.table_name
        """
        self.table_name = self.file[1][0][:self.file[1][0].index(" ")]

    def check_for_table_stake(self):
        """
        Check for table stake from first hand
        :return: self.table_stake
        """
        self.table_stake = self.file[0][0][self.file[0][0].index("$"):-26]

    def check_for_table_size(self):
        """
        Check for table size from first hand
        :return: self.table_size
        """
        self.table_size = self.file[1][0][self.file[1][0].index("-") - 1]

    def check_date(self):
        """
        Check for date of first hand
        :return: self.date
        """
        self.date = self.file[0][0][-21:-13]

    def check_hands(self, ind):
        """
        Get hand number and hand start time, set into dict 'hands'
        Get number of hands played in session from getting length of self.hands dict
        :param ind: Current row number
        :return: self.hands, self.no_of_hands
        """
        self.hand_no = self.file[ind][0][self.file[ind][0].index("#") + 1:self.file[ind][0].index("-") - 1]
        self.hand_start = self.file[ind][0][-12:-4]
        self.hands[self.file[ind][0][self.file[ind][0].index("#") + 1:self.file[ind][0].index("-") - 1]] = \
            self.file[ind][0][-12:-4]
        self.no_of_hands = len(self.hands)

    def check_time_played(self):
        """
        Get first hand start time and last hand start time, find time difference between the two
        :return: session_time
        """
        time_start = datetime.datetime.strptime(list(self.hands.values())[0], '%H:%M:%S')
        end_time = datetime.datetime.strptime(list(self.hands.values())[-1], '%H:%M:%S')
        self.session_time = end_time - time_start

    def get_results(self, ind, user):
        """
        Check if 'user' is in current line, if so, check for variations such as ' calls ' or ' won '.
        Gets the total amount wagered (or returned) and then if the hand is lost, returns that amount;
        if the hand is won, takes away the amount wagered from the pot total to reflect profit.
        :param ind: current file row
        :param user: username
        :return: results of the hand
        """
        if '($' in self.file[ind][0]:
            if f'returned to {user}' in self.file[ind][0]:
                self.bet_return = float(
                    self.file[ind][0][self.file[ind][0].index("(") + 2:self.file[ind][0].index(")")])
                print(f"bet_return = {self.bet_return}")
        elif ' small blind ' in self.file[ind][0]:
            self.small = float(self.file[ind][0][self.file[ind][0].index("$") + 1:])
            print(f"small = {self.small}")
        elif ' big blind ' in self.file[ind][0]:
            self.big = float(self.file[ind][0][self.file[ind][0].index("$") + 1:])
            print(f"big = {self.big}")
        elif ' calls ' in self.file[ind][0]:
            self.call_bet += float(self.file[ind][0][self.file[ind][0].index("$") + 1:
                                                     self.file[ind][0].index(".") + 3])
            print(f"call_bet = {self.call_bet}")
        elif ' bets ' in self.file[ind][0]:
            self.call_bet += float(self.file[ind][0][self.file[ind][0].index("$") + 1:self.file[ind][0].index(".") + 3])
            print(f"call_bet = {self.call_bet}")
        elif ' raises ' in self.file[ind][0]:
            self._raise = float(self.file[ind][0][self.file[ind][0].index("$") + 1:
                                                  self.file[ind][0].index(" ", self.file[ind][0].index("$"))])
            print(f"_raise = {self._raise}")
        elif ' folds' in self.file[ind][0]:
            self.result = (self.small + self.big + self.call_bet + self._raise) * -1
            print(f"result = {self.result}")
        elif ' lost ' in self.file[ind][0]:
            self.result = (self.small + self.big + self.call_bet + self._raise) * -1
            print(f"result = {self.result}")
        elif ' won ' in self.file[ind][0]:
            self.won = float(self.file[ind][0][self.file[ind][0].index("$") + 1:self.file[ind][0].index(".") + 3])
            self.actions = float(
                self.small) + float(self.big) + float(self.call_bet) + float(self._raise) - float(self.bet_return)
            print(f"actions = {round(self.actions, 2)}")
            self.result = round(self.won, 2) - round(self.actions, 2)
            print(f"result = {self.result}")
        self.hand_results.append(self.result)

    def new_hand(self):
        self.small = 0
        self.big = 0
        self.call_bet = 0
        self.bet_return = 0
        self._raise = 0 - self.bet_return
        self.won = 0
        self.actions = 0
        self.result = 0
        # print("\n\nNew hand...")

    def insert_session_data(self):
        try:
            session_insert = "INSERT INTO Sessions " \
                             "SELECT %s, %s, %s, %s, %s " \
                             "WHERE NOT EXISTS " \
                             "(SELECT SessionTable, SessionDate, SessionTime, SessionHands, SessionResults " \
                             "FROM Sessions " \
                             "WHERE SessionTable = %s AND SessionDate = %s AND SessionTime = %s AND SessionHands = %s " \
                             "AND SessionResults = %s)"
            cursor.execute(session_insert, (
                self.table_name, self.date, self.session_time, self.no_of_hands, sum(self.hand_results),
                self.table_name, self.date, self.session_time, self.no_of_hands, sum(self.hand_results)))
            sql_connection.commit()
            print("Session Data inserted successfully")
        except errorcode as err:
            print(f"Error: {err}")


class Table:
    def __init__(self, table_name, table_stake, table_size, table_date):
        self.table_name = table_name
        self.table_stake = table_stake
        self.table_size = table_size
        self.table_date = table_date
        self.total_time_played = str
        self.times_played = int
        self.hands_played = int
        self.results = float

    def __str__(self):
        return str(self.__dict__)

    def insert_table_data(self):
        try:
            table_insert = "INSERT INTO PokerTables " \
                           "SELECT %s, %s, %s, %s " \
                           "WHERE NOT EXISTS " \
                           "(SELECT TableName, TableStake, TableSize, TableDate " \
                           "FROM PokerTables " \
                           "WHERE TableName = %s AND TableStake = %s AND TableSize = %s AND TableDate = %s)"
            cursor.execute(table_insert, (self.table_name, self.table_stake, self.table_size, self.table_date,
                                          self.table_name, self.table_stake, self.table_size, self.table_date))
            sql_connection.commit()
            print("Table Data inserted successfully")
        except errorcode as err:
            print(f"Error: {err}")


class Player:
    def __init__(self, player_name):
        self.player_name = player_name
        self.sessions_played = int
        self.hands_played = int
        self.results = float

    def __str__(self):
        return str(self.__dict__)

    def insert_player_data(self):
        try:
            player_insert = "INSERT INTO Players " \
                            "SELECT %s " \
                            "WHERE NOT EXISTS " \
                            "(SELECT PlayerName FROM Players " \
                            "WHERE PlayerName = %s)"
            cursor.execute(player_insert, (self.player_name, self.player_name))
            sql_connection.commit()
            print("Player Data inserted succesfully")
        except errorcode as err:
            print(f"Error: {err}")


class Hand:
    def __init__(self, hand_number, date, result):
        self.hand_number = hand_number
        self.date = date
        self.result = result

    def __str__(self):
        return str(self.__dict__)

    def insert_hand_data(self):
        try:
            hand_insert = "INSERT INTO Hands " \
                          "SELECT %s, %s, %s " \
                          "WHERE NOT EXISTS " \
                          "(SELECT HandNumber, HandDate, HandResults FROM Hands " \
                          "WHERE HandNumber = %s AND HandDate = %s AND HandResults = %s)"
            cursor.execute(hand_insert, (self.hand_number, self.date, self.result,
                                         self.hand_number, self.date, self.result))
            sql_connection.commit()
            print("Hand Date Inserted Succesfully")
        except errorcode as err:
            print(f"Error: {err}")


if __name__ == '__main__':
    try:
        cursor.execute(f"USE {HAND_HISTORY_DB_NAME}")
        print(f"Database: {HAND_HISTORY_DB_NAME}")
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
    # sql_connection.close()
    # cursor.close()

    dir = HistoryDirectory("PolarFox")
    dir.find_profile_history()
    for file in range(0, len(dir.session_files)):
        session_file = open(dir.session_files[file], 'r')
        file_reader = list(csv.reader(session_file, delimiter="\n"))

        sess = Session(file_reader)
        sess.check_for_table_name()
        sess.check_for_table_stake()
        sess.check_for_table_size()
        sess.check_date()

        tabl = Table(sess.table_name, sess.table_stake, sess.table_size, sess.date)
        plyr = Player(dir.user_name)

        tabl.insert_table_data()
        plyr.insert_player_data()

        counter = 0
        while counter != len(file_reader):
            file = FileRow(file_reader[counter])
            if file.check_row("Hand #"):
                sess.new_hand()
                sess.check_hands(counter)
                print(sess.table_name)
                print(sess.table_stake)
                print(sess.table_size)
                print(sess.date)
                print(sess.hand_no)
                print(sess.hand_start)
                counter += 1
            elif file.check_row(str(dir.user_name)):
                sess.get_results(counter, dir.user_name)
                counter += 1
            elif not file_reader[counter]:
                hand = Hand(sess.hand_no, sess.date, sess.result)
                hand.insert_hand_data()
                counter += 1
            else:
                print(file)
                counter += 1

        print(f"total result: {sum(sess.hand_results)}")
        sess.check_time_played()
        sess.insert_session_data()
        print(f"time played: {sess.session_time}")
