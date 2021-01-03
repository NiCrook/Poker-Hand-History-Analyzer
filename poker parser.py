"""
EXAMPLE HAND:

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
"""

#   Need to seperate: hand number, game type, stakes, time and date, table name, table size, where the button is
#   each seat with the player name and player stack size, the small blind and big blind posting the blinds
#   being deal the hole cards, the preflop action, then the flop cards, then the flop actions
#   then the turn cards, then the turn action, then the river cards, then the river actions
#   showdown, which is the (main) pot with rake, then each player's holding, then the winner(s) collection the pot(s)
#   summary, the total pot size with rake and jackpot, the total board seen, what each seat had and won/lost
#   unless that player folded, which they are just noted as not having bet

# IMPORT
import csv
import re

# PLACEHOLDER VARIABLES
INDEX = 0
HAND_NO = 0
GAME_TYPE = ""
LIMIT_TYPE = ""
STAKE_SIZE = ""
TIME = ""
DATE = ""
TABLE_NAME = ""
TABLE_SIZE = 0
BUTTON_POSITION = 0
PLAYER_NAME = ""
PLAYER_SEAT = 0
PLAYER_STACK = 0
PLAYERS = {}  # name: [seat, stack]
HANDS = {}

# HAND HISTORY LOCATION
HAND_HISTORY = r"C:\AmericasCardroom\handHistory\PolarFox\HH20201106 CASHID-G22721376T18 TN-Powhattan GAMETYPE-Omaha " \
               r"LIMIT-no CUR-REAL OND-F BUYIN-0 MIN-1 MAX-2.txt "

# CSV PARSING
with open(HAND_HISTORY, 'r') as csv_file:
    csv_reader = list(csv.reader(csv_file, delimiter="\n"))
    while INDEX != len(csv_reader):
        csv_reader[INDEX] = re.sub("- |[|] ", "", str(csv_reader[INDEX]))
        if "Hand" in str(csv_reader[INDEX]):
            HAND_NO = csv_reader[INDEX] \
                [csv_reader[INDEX].index("#") + 1:csv_reader[INDEX].index(" ", csv_reader[INDEX].index("#"))]
            STAKE_SIZE = csv_reader[INDEX] \
                [csv_reader[INDEX].index("$"):csv_reader[INDEX].index(" ", csv_reader[INDEX].index("$"))]
            TIME = csv_reader[INDEX][csv_reader[INDEX].index(":") - 2:csv_reader[INDEX].index("UTC") + 3]
            DATE = csv_reader[INDEX][csv_reader[INDEX].index("/", csv_reader[INDEX].index("/") + 1) - 4:-15]
        if "Omaha" in str(csv_reader[INDEX]):
            GAME_TYPE = "Omaha"
        if "No Limit" in str(csv_reader[INDEX]):
            LIMIT_TYPE = "No Limit"
            HANDS[HAND_NO] = [GAME_TYPE, LIMIT_TYPE, STAKE_SIZE, DATE, TIME]
        if "-max" in csv_reader[INDEX]:
            TABLE_NAME = csv_reader[INDEX][2:csv_reader[INDEX].index(" ")]
            TABLE_SIZE = csv_reader[INDEX][csv_reader[INDEX].index(" ") + 1:csv_reader[INDEX].index(" ", csv_reader[
                INDEX].index(" ") + 1)]
            BUTTON_POSITION = csv_reader[INDEX][csv_reader[INDEX].index("#") + 1]
        if "Seat" in csv_reader[INDEX]:
            if "and" not in csv_reader[INDEX]:
                if "is the button" not in csv_reader[INDEX]:
                    if "folded on" not in csv_reader[INDEX]:
                        if "will be allowed" not in csv_reader[INDEX]:
                            PLAYER_NAME = csv_reader[INDEX][csv_reader[INDEX].index(":") + 2:
                                                            csv_reader[INDEX].index("(") - 1]
                            PLAYER_SEAT = csv_reader[INDEX][csv_reader[INDEX].index(" ") + 1]
                            PLAYER_STACK = csv_reader[INDEX][csv_reader[INDEX].index("$") + 1:
                                                             csv_reader[INDEX].index(")")]
                            PLAYERS[PLAYER_NAME] = [PLAYER_SEAT, PLAYER_STACK]
        HANDS[HAND_NO] = [TABLE_NAME, TABLE_SIZE, BUTTON_POSITION, GAME_TYPE, LIMIT_TYPE, STAKE_SIZE, TIME, DATE]
        INDEX += 1
