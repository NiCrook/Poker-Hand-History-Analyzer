# IMPORT
import csv
import datetime
from getpass import getpass
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import mysql.connector as mysql
from mysql.connector import errorcode
import os
import tkinter as tk
from tkinter import StringVar, IntVar

### ESTABLISH SQL CONNECTION
sql_connection = mysql.connect(
    host="localhost",
    user="root",
    password="password"
)
cursor = sql_connection.cursor(buffered=True)

# ESTABLISH SQL DATABASE/TABLES
HAND_HISTORY_DB_NAME = 'HandHistory'
HAND_HISTORY_DB_TABLES = {}
HAND_HISTORY_DB_TABLES['Sessions'] = (
    "CREATE TABLE `Sessions` ("
    "   `SessionID` int NOT NULL AUTO_INCREMENT PRIMARY KEY,"
    "   `SessionTable` varchar(36),"
    "   `SessionDate` date NOT NULL,"
    "   `SessionTime` time NOT NULL,"
    "   `SessionHands` int,"
    "   `SessionResults` float,"
    "   CONSTRAINT `SessionUnique` UNIQUE (SessionTable, SessionDate, SessionTime, SessionHands, SessionResults)"
    ")  ENGINE=InnoDB")
HAND_HISTORY_DB_TABLES['Tables'] = (
    "CREATE TABLE `PokerTables` ("
    "   `TableName` varchar(36) PRIMARY KEY,"
    "   `TableStake` varchar(16),"
    "   `TableSize` int,"
    "   `TableDate` date NOT NULL"
    ") ENGINE=InnoDB")
HAND_HISTORY_DB_TABLES['Hands'] = (
    "CREATE TABLE `Hands` ("
    "   `HandID` int NOT NULL AUTO_INCREMENT PRIMARY KEY,"
    "   `HandNumber` int UNIQUE,"
    "   `HandDate` date NOT NULL,"
    "   `HandResults` float"
    ") ENGINE=InnoDB")
HAND_HISTORY_DB_TABLES['Players'] = (
    "CREATE TABLE `Players` ("
    "   `PlayerName` varchar(16) PRIMARY KEY,"
    # "   `PlayerSessions` int,"
    # "   `PlayerHands` int,"
    "   `PlayerResults` float"
    ") ENGINE=InnoDB")


def create_sql_database(cursor, db_name):
    """
    Create target SQL database
    :param cursor:
    :param db_name: target database name
    :return: database creation
    """
    try:
        cursor.execute(f"CREATE DATABASE {db_name} DEFAULT CHARACTER SET 'utf8'")
    except mysql.Error as err:
        print(f"Failed to create database: {err}\n")
        exit(1)


### DIRECTORY
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


### FILE ROW CHECK
class FileRow:
    def __init__(self, file):
        """
        Get a specific row from a specific file
        :param file_name: Get file name to use
        :return: True if string_check is found
        """
        self.file = file

    def __str__(self):
        return str(self.__dict__)

    def check_row(self, string_check):
        """
        Check current row for string_check presence
        :param string_check: target string to check
        :return: True if string_check is found
        """
        if not self.file:
            pass
        else:
            if string_check in self.file[0]:
                return True


### HAND PARSING
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
        self.hand_culm_results = []

        self.small = 0
        self.big = 0
        self.call_bet = 0
        self.bet_return = 0
        self._raise = 0 - self.bet_return
        self.won = 0
        self.actions = 0
        self.result = 0

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
        elif ' small blind ' in self.file[ind][0]:
            self.small = float(self.file[ind][0][self.file[ind][0].index("$") + 1:])
        elif ' big blind ' in self.file[ind][0]:
            self.big = float(self.file[ind][0][self.file[ind][0].index("$") + 1:])
        elif ' calls ' in self.file[ind][0]:
            self.call_bet += float(self.file[ind][0][self.file[ind][0].index("$") + 1:
                                                     self.file[ind][0].index(".") + 3])
        elif ' bets ' in self.file[ind][0]:
            self.call_bet += float(self.file[ind][0][self.file[ind][0].index("$") + 1:self.file[ind][0].index(".") + 3])
        elif ' raises ' in self.file[ind][0]:
            self._raise = float(self.file[ind][0][self.file[ind][0].index("$") + 1:
                                                  self.file[ind][0].index(" ", self.file[ind][0].index("$"))])
        elif ' folds' in self.file[ind][0]:
            self.result = (self.small + self.big + self.call_bet + self._raise) * -1
        elif ' lost ' in self.file[ind][0]:
            self.result = (self.small + self.big + self.call_bet + self._raise) * -1
        elif ' won ' in self.file[ind][0]:
            self.won = float(self.file[ind][0][self.file[ind][0].index("$") + 1:self.file[ind][0].index(".") + 3])
            self.actions = float(
                self.small) + float(self.big) + float(self.call_bet) + float(self._raise) - float(self.bet_return)
            self.result = round(self.won, 2) - round(self.actions, 2)
        self.hand_results.append(self.result)

    def get_culm_results(self):
        counter = 0
        previous_result = 0
        while counter != len(self.hand_results):
            self.hand_culm_results.append(previous_result + self.hand_results[counter])
            previous_result = self.hand_culm_results[-1]
            counter += 1

    def new_hand(self):
        """
        Reset all hand-related variables to 0
        :return:
        """
        self.small = 0
        self.big = 0
        self.call_bet = 0
        self.bet_return = 0
        self._raise = 0 - self.bet_return
        self.won = 0
        self.actions = 0
        self.result = 0

    def insert_session_data(self):
        """
        Insert Session data - table name, session date, time of session, number of hands played in session, and results
        :return: Insert data into table Sessions
        """
        try:
            session_insert = "INSERT INTO Sessions (SessionTable, SessionDate, SessionTime, SessionHands, " \
                             "SessionResults) " \
                             "VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(session_insert, (
                self.table_name, self.date, self.session_time, self.no_of_hands, sum(self.hand_results)))
            sql_connection.commit()
            print("Session Data inserted successfully")
        except mysql.IntegrityError as err:
            print(f"Error: {err}")


class Table:
    def __init__(self, table_name, table_stake, table_size, table_date):
        """
        Establish Table data
        :param table_name:
        :param table_stake:
        :param table_size:
        :param table_date:
        """
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
        """
        Insert Table data - table name, table stake, table size, and date played on table
        :return:
        """
        try:
            table_insert = "INSERT INTO PokerTables VALUES (%s, %s, %s, %s)"
            cursor.execute(table_insert, (self.table_name, self.table_stake, self.table_size, self.table_date))
            sql_connection.commit()
            print("Table Data inserted successfully")
        except mysql.IntegrityError as err:
            print(f"Error: {err}")


class Player:
    def __init__(self, player_name):
        """
        Establish player data
        :param player_name:
        """
        self.player_name = player_name
        self.sessions_played = int
        self.hands_played = int
        self.results = float

    def __str__(self):
        return str(self.__dict__)

    def insert_player_name(self):
        """
        Insert Player Name
        :return:
        """
        try:
            name_insert = "INSERT INTO Players (PlayerName) VALUES (%s)"
            cursor.execute(name_insert, (self.player_name,))
            sql_connection.commit()
            print("Player Name inserted succesfully")
        except mysql.IntegrityError as err:
            print(f"Error: {err}")

    def update_player_results(self):
        """
        Insert Player Results
        :return:
        """
        try:
            result_insert = "UPDATE Players " \
                            "SET PlayerResults = (SELECT ROUND(SUM(SessionResults), 2) FROM Sessions) " \
                            "WHERE PlayerName = %s"
            cursor.execute(result_insert, (self.player_name,))
            sql_connection.commit()
            print("Player Results inserted succesfully")
        except mysql.IntegrityError as err:
            print(f"Error: {err}")


class Hand:
    def __init__(self, hand_number, date, result):
        """
        Establish Hand data
        :param hand_number:
        :param date:
        :param result:
        """
        self.hand_number = hand_number
        self.date = date
        self.result = result

    def __str__(self):
        return str(self.__dict__)

    def insert_hand_data(self):
        """
        Insert Hand data - hand number, date of hand played, result
        :return:
        """
        try:
            hand_insert = "INSERT INTO Hands (HandNumber, HandDate, HandResults) VALUES (%s, %s, %s)"
            cursor.execute(hand_insert, (self.hand_number, self.date, self.result))
            sql_connection.commit()
            print("Hand Data Inserted Succesfully")
        except mysql.IntegrityError as err:
            print(f"Error: {err}")


## TKINTER FRAME
class MainFrame:
    def __init__(self, master):
        self.master = master
        master.title = "Poker Hand History Analyzer"

        cursor.execute("SELECT PlayerName FROM Players")
        self.player_name = cursor.fetchall()
        cursor.execute("SELECT HandID FROM Hands ORDER BY HandID DESC LIMIT 1")
        self.no_hands = cursor.fetchall()
        cursor.execute("SELECT SessionID FROM Sessions ORDER BY SessionID DESC LIMIT 1")
        self.no_sess = cursor.fetchall()
        cursor.execute("SELECT ROUND(SUM(SessionResults), 2) FROM Sessions")
        self.results = cursor.fetchall()

        self.pn_var = StringVar()
        self.hn_var = IntVar()
        self.sn_var = IntVar()
        self.results_var = IntVar()

        self.pn_var.set(self.player_name)
        self.hn_var.set(self.no_hands)
        self.sn_var.set(self.no_sess)
        self.results_var.set(self.results)

        self.player_buttons = {
            'import': tk.Button(self.master, text="Import", command=self.import_hands),
            'hands_filter': tk.Button(self.master, text="Hands", command=lambda: self.build_graph("hand_button")),
            'sessions_filter': tk.Button(self.master, text='Sessions',
                                         command=lambda: self.build_graph("session_button")),
            'quit': tk.Button(self.master, text="Quit", command=exit)
        }

        self.player_labels = {
            'stats': tk.Label(self.master, text="Statistics"),
            'player_name': tk.Label(self.master, text="Player Name:"),
            'no_hands': tk.Label(self.master, text="Number of Hands:"),
            'no_sessions': tk.Label(self.master, text="Number of Sessions:"),
            'player_results': tk.Label(self.master, text="Player Results:"),
            'hand_results_graph': tk.Label(self.master, text="Hand Results"),
            'session_results_graph': tk.Label(self.master, text="Session Results"),
            'import_successful': tk.Label(self.master, text="Import successful!"),
            'hand_list': tk.Label(self.master, text="Hand List"),
            'session_list': tk.Label(self.master, text="Session List"),
            'filters': tk.Label(self.master, text="Filters"),
            'pn_var_label': tk.Label(self.master, textvariable=self.pn_var),
            'hn_var_label': tk.Label(self.master, textvariable=self.hn_var),
            'sn_var_label': tk.Label(self.master, textvariable=self.sn_var),
            'results_var_label': tk.Label(self.master, textvariable=self.results_var)
        }

        self.player_labels['player_name'].grid(row=0, column=0)
        self.player_labels['no_hands'].grid(row=0, column=2)
        self.player_labels['no_sessions'].grid(row=0, column=4)
        self.player_labels['player_results'].grid(row=0, column=6)

        self.player_labels['pn_var_label'].grid(row=0, column=1)
        self.player_labels['hn_var_label'].grid(row=0, column=3)
        self.player_labels['sn_var_label'].grid(row=0, column=5)
        self.player_labels['results_var_label'].grid(row=0, column=7)

        self.player_buttons['hands_filter'].grid(row=1, column=0)
        self.player_buttons['sessions_filter'].grid(row=1, column=1)
        self.player_buttons['import'].grid(row=1, column=2)
        self.player_buttons['quit'].grid(row=1, column=3)

    def import_hands(self):
        for file in range(0, len(dir.session_files)):
            session_file = open(dir.session_files[file], 'r')
            file_reader = list(csv.reader(session_file, delimiter="\n"))

            sess = Session(file_reader)
            sess.check_for_table_name()
            sess.check_for_table_stake()
            sess.check_for_table_size()
            sess.check_date()

            tabl = Table(sess.table_name, sess.table_stake, sess.table_size, sess.date)

            tabl.insert_table_data()
            plyr.insert_player_name()

            counter = 0
            while counter != len(file_reader):
                file = FileRow(file_reader[counter])
                if file.check_row("Hand #"):
                    sess.new_hand()
                    sess.check_hands(counter)
                    counter += 1
                elif file.check_row(str(dir.user_name)):
                    sess.get_results(counter, dir.user_name)
                    counter += 1
                elif not file_reader[counter]:
                    hand = Hand(sess.hand_no, sess.date, sess.result)
                    hand.insert_hand_data()
                    counter += 1
                else:
                    counter += 1

            sess.get_culm_results()
            sess.check_time_played()
            sess.insert_session_data()
        plyr.update_player_results()
        self.player_labels['import_successful'].grid(row=1, column=4)

    def build_graph(self, button):
        fig = Figure(figsize=(5, 5), dpi=100)
        graph = fig.add_subplot(111)
        if button == "hand_button":
            cursor.execute("SELECT HandID FROM Hands ORDER BY HandID ASC")
            no_hands_query = cursor.fetchall()
            self.x = [int(result) for (result,) in no_hands_query]
            self.x.insert(0, 0)

            cursor.execute("SELECT HandResults FROM Hands ORDER BY HandID ASC")
            hand_results_query = cursor.fetchall()
            hand_results = [float(result) for (result,) in hand_results_query]
            self.y = [0]
            previous_result = 0
            for result in hand_results:
                self.y.append(previous_result + result)
                previous_result = self.y[-1]
            graph.set_xlabel("Hands Played")
            graph.set_ylabel("Total Results in $")
        elif button == "session_button":
            cursor.execute("SELECT SessionID FROM Sessions ORDER BY SessionID ASC")
            no_sess_query = cursor.fetchall()
            self.x = [int(result) for (result,) in no_sess_query]
            self.x.insert(0, 0)

            cursor.execute("SELECT SessionResults FROM Sessions ORDER BY SessionID ASC")
            sess_results_query = cursor.fetchall()
            results = [float(result) for (result,) in sess_results_query]
            self.y = [0]
            previous_result = 0
            for result in results:
                self.y.append(previous_result + result)
                previous_result = self.y[-1]
            graph.set_xlabel("Sessions Played")
            graph.set_ylabel("Total Results in $")

        graph.plot(self.x, self.y)

        canvas = FigureCanvasTkAgg(fig, self.master)
        canvas.get_tk_widget().grid(row=2, column=0, columnspan=8)

    def exit_frame(self):
        self.master.quit()
        self.master.destroy()


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

    dir = HistoryDirectory("PolarFox")
    dir.find_profile_history()
    plyr = Player(dir.user_name)
    window = tk.Tk()
    gui = MainFrame(window)
    window.mainloop()
