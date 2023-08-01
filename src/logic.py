from aiogram.types import (
	Message, CallbackQuery,
	InlineKeyboardMarkup, InlineKeyboardButton
)

from main import bot
import random as rd
from copy import deepcopy as copy


team_next_round, move, choosed_pawn = None, None, None

red_c, blue_c = 0, 0
red_alive, blue_alive = True, True

win = ''

may_moves = []

teams = {
	'red': ["", 0],
	'blue': ["", 0] # 1004461367
}

game_field = [
	['🔺', '.', '.', '.', '.', '.', '.', '🔹'],
	['🔺', '.', '.', '.', '.', '.', '.', '🔹'],
	['🔺', '.', '.', '.', '.', '.', '.', '🔹'],
	['🔺', '.', '.', '.', '.', '.', '.', '🔹'],
	['🏰', '.', '.', '.', '.', '.', '.', '🏯'],
	['🔺', '.', '.', '.', '.', '.', '.', '🔹'],
	['🔺', '.', '.', '.', '.', '.', '.', '🔹'],
	['🔺', '.', '.', '.', '.', '.', '.', '🔹'],
	['🔺', '.', '.', '.', '.', '.', '.', '🔹'],
]


# функция вычисляющая пешку которая находится дальше всего к своему замку
def calc_distance(team):
	sym = '🔺' if team == 'red' else '🔹'
	distances = []

	if team == 'red':
		for y in range(9):
			for x in range(8):
				if game_field[y][x] == sym:
					distances.append(x)
	else:
		for y in range(9):
			for x in range(7, -1, -1):
				if game_field[y][x] == sym:
					distances.append(7-x)

	return distances

# функция возвращает True если колв-о пешек от края на 3 позиции >= 3
def can_move_back(team):
	d = calc_distance(team)
	
	for i in range(len(d)):
		if d[i] < 4: d[i] = 0 

	return d.count(4) >= 1

# функция подсчитывает кол-во пешек данной команды
def count_pawns(team):
	sym = '🔺' if team == 'red' else '🔹'
	count = 0

	for pawns in game_field:
		for pawn in pawns:
			if pawn == sym:
				count += 1

	return count

# функция ловит возможную ошибку, служит для уменьшения и читаемости кода	
def catch(x, y):
	try:
		return game_field[y][x]
	except IndexError:
		return None

# просто возвращает противника данной команды
def enemy(team):
	return 'blue' if team == 'red' else 'red'

# возвращает вариацию слова "пешка" в множественном числе, зависит от числа
def string_num(num):
	if num == 1:
		return 'пешка'
	elif num in [2, 3, 4]:
		return 'пешки'
	else:
		return 'пешек'

# упрощает код где нужно выводить кол-во пешек в замке
# и возвращает "замок разрушен" если он разрушен
def castle_pawns_count(team):
	if team == 'red' and red_alive:
		return f'{red_c} {string_num(red_c)}'
	elif team == 'blue' and blue_alive:
		return f'{blue_c} {string_num(blue_c)}'
	else:
		return 'замок разрушен'


# заканчивает игру и предлагает начать новую, так же выводит победителя
async def alert_win(query: CallbackQuery):
	text = f"""
***__The Castle Game__***

***Игроки:***
    🔴 `{teams['red'][0]}`
    🔵 `{teams['blue'][0]}`

***Победитель:*** {'🔴' if win == 'red' else '🔵'} `{teams[win][0]}`		   
	"""
	
	keyboard = [[InlineKeyboardButton("Играть снова", callback_data='play_again')]]
	
	markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
	
	await bot.edit_message_text(text, inline_message_id=query.inline_message_id, reply_markup=markup)
	
# изменяет текст и/или клавиатуру сообщения
async def rewrite(query: CallbackQuery, team):
	text = f"""
***__The Castle Game__***

***Игроки:***
    🔴 `{teams['red'][0]}`
    🔵 `{teams['blue'][0]}`

***Замки:***
    🏰: `{castle_pawns_count('red')}`
    🏯: `{castle_pawns_count('blue')}`

***Ходит:*** `{teams[team][0]}`
***Можно сделать {move} {'шаг' if move == 1 else 'шага'}***
	"""

	keyboard = copy(game_field)

	for y in range(9):
		for x in range(8):
			keyboard[y][x] = InlineKeyboardButton(f" {keyboard[y][x]} ", callback_data=f'{keyboard[y][x]}_{x}_{y}')

	markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

	await bot.edit_message_text(text, inline_message_id=query.inline_message_id, reply_markup=markup)

# выбор команды: красная/синяя
async def set_team(query: CallbackQuery, team):
	if team != 'again':
		if teams[team][1] != 0 and teams[team][1] != query.from_user.id:
			await query.answer("Эта команда уже занята.")
		elif teams[team][1] == query.from_user.id:
			teams[team] = ["", 0]
		else:
			if teams[enemy(team)][1] == query.from_user.id: teams[enemy(team)] = ["", 0]
			teams[team] = [query.from_user.first_name, query.from_user.id]

	text = f"""
***__The Castle Game__***

***Игроки:***
    🔴 `{teams['red'][0]}`
    🔵 `{teams['blue'][0]}`

***Выбор команд:***
	"""

	keyboard = [
		[
			InlineKeyboardButton(" 🔴 ", callback_data='red_team'),
			InlineKeyboardButton(" 🔵 ", callback_data='blue_team')
   		],
		[
			InlineKeyboardButton("Играть", callback_data='play')
		]
	]

	markup = InlineKeyboardMarkup(inline_keyboard=keyboard, row_width=2)

	await bot.edit_message_text(text, inline_message_id=query.inline_message_id, reply_markup=markup)

# начало игры (генерация поля)
async def start_play(query: CallbackQuery):
	global team_next_round, move

	if teams['blue'][1] == 0 or teams['red'][1] == 0:
		await query.answer("Не все команды заполнены.")
		return
	
	team = team_next_round = rd.choice(['red', 'blue'])
	move = rd.randint(1, 3)

	await rewrite(query, team)

# проверка победы
async def check_win(query, team):
	global win
	
	if (not red_alive) or (not blue_alive):
		if team == 'red' and count_pawns('blue') == 0:
			win = 'red'
			await alert_win(query)
			return True
		elif team == 'blue' and count_pawns('red') == 0:
			win = 'blue'
			await alert_win(query)
			return True
	
	return False

# если пешка не выбрана(choosed_pawn), то будет выбрана
# но если пешка уже выбрана, будет возможность ею походить
async def pawn_move(query: CallbackQuery):
	global team_next_round, move, choosed_pawn, may_moves
	global red_c, blue_c, castle_move
	global red_alive, blue_alive


	pawn_sym, x, y = query.data.split('_')
	x, y = int(x), int(y)
	team = 'red' if teams['red'][1] == query.from_user.id else 'blue'


	if win != '': return

	if team != team_next_round:
		await query.answer("Сейчас ходит другой игрок.")
		return

	# выбор пешки
	if choosed_pawn is None:
		if pawn_sym in (['🏯', '🔹'] if team == 'red' else ['🏰', '🔺']):
			await query.answer("Этой пешкой нельзя ходить.")
			return
		elif pawn_sym == '.':
			await query.answer("Выберите пешку.")
			return

		choosed_pawn = query.data

		may_moves.append(f"{catch(x, y+move)}_{x}_{y+move}")
		may_moves.append(f"{catch(x+move, y+move)}_{x+move}_{y+move}")
		may_moves.append(f"{catch(x+move, y)}_{x+move}_{y}")
		may_moves.append(f"{catch(x+move, y-move)}_{x+move}_{y-move}")
		may_moves.append(f"{catch(x, y-move)}_{x}_{y-move}")
		may_moves.append(f"{catch(x-move, y-move)}_{x-move}_{y-move}")
		may_moves.append(f"{catch(x-move, y)}_{x-move}_{y}")
		may_moves.append(f"{catch(x-move, y+move)}_{x-move}_{y+move}")

		# await query.answer("Пешка выбрана.")
		# print(may_moves)

	# ход
	else:
		if pawn_sym in (['🔺', '🏰'] if team == 'red' else ['🔹', '🏯']):
			choosed_pawn = None
			may_moves.clear()
			await pawn_move(query)
			return

		if query.data not in may_moves:
			await query.answer("Сюда нельзя ходить.")
			return

		c_sym, c_x, c_y = choosed_pawn.split('_')
		c_x, c_y = int(c_x), int(c_y)

		if c_sym == ('🏰' if team == 'red' else '🏯'):
			if (red_c if team == 'red' else blue_c) == 0:
				await query.answer("В замке нету пешек для хода.")
				return


		if not (c_sym == ('🏰' if team == 'red' else '🏯')):
			game_field[c_y][c_x] = '.'

		game_field[y][x] = c_sym.replace('🏰', '🔺').replace('🏯', '🔹')

		if c_sym == ('🏰' if team == 'red' else '🏯'):
			if team == 'red': red_c -= 1
			else: blue_c -= 1
		
		if pawn_sym == ('🔹' if team == 'red' else '🔺'):
			if team == 'red': blue_c += 1
			else: red_c += 1

		elif pawn_sym == ('🏯' if team == 'red' else '🏰'):
			if team == 'red' and blue_c == 0:
				blue_alive = False
			elif team == 'blue' and red_c == 0:
				red_alive = False
			
			else:
				if team == 'red':
					red_c += 1
					blue_c -= 1
				else:
					blue_c += 1
					red_c -= 1
					
				game_field[y][x] = '🏯' if team == 'red' else '🏰'

			if await check_win(query, team): return

		if await check_win(query, team): return


		choosed_pawn = None
		may_moves.clear()

		team_next_round = 'red' if team == 'blue' else 'blue'
		move = rd.randint(1, 3)

		await rewrite(query, team_next_round)
