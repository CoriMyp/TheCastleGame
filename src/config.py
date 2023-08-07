import sqlite3 as sql
import colorama as cl
import os

# colorama init
cl.init()


# BOT TOKEN
# TOKEN = open('./token.txt', 'r', encoding='utf-8').readline()
TOKEN = os.environ['token']


# SQL TABLE WITH USER'S SETTINGS (on future)
db = sql.connect("castle.db")
cursor = db.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS settings(
	user_id INT,

	lang TEXT,
	move_counts INT,
	type_of_game INT,

	red_pawn TEXT,
	red_castle TEXT,
	blue_pawn TEXT, 
	blue_castle TEXT
)""")


# log func
def log(title, msg=None):
	if msg:
		print(cl.Fore.RED + f"[LOG] {title}: " + str(msg) + cl.Fore.RESET)
	else:
		print(cl.Fore.RED + f"[LOG] {title}" + cl.Fore.RESET)
