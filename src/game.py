from aiogram.types import (
	Message, CallbackQuery,
	InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.utils.exceptions import MessageNotModified

import random as rd
from copy import deepcopy as copy

from main import bot
from src.functions import *
from src.config import log
from src.classes import *


games = ActiveGames()

# заканчивает игру и предлагает начать новую, так же выводит победителя
async def alert_win(query: CallbackQuery):
	game = games.get(query.inline_message_id)

	text = f"""
***__The Castle Game {game.type}x{game.type}__***

***Игроки:***
    🔴 `{', '.join([plr.name for plr in game.teams['red']])}`
    🔵 `{', '.join([plr.name for plr in game.teams['blue']])}`

***Победител{'ь' if game.type == 1 else 'и'}:*** {'🔴' if game.winner == 'red' else '🔵'} {' '.join([f"`{plr.name}`" for plr in game.teams[game.winner]])}
	"""
	
	keyboard = [[InlineKeyboardButton("Играть снова", callback_data=f'{game.type} play_again')]]
	
	markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
	
	await bot.edit_message_text(text, inline_message_id=query.inline_message_id, reply_markup=markup)

# проверка победы
async def check_win(query: CallbackQuery):
	game = games.get(query.inline_message_id)

	if not game.red_alive and count_pawns(game.field, 'red') == 0:
		game.winner = 'blue'
	elif not game.blue_alive and count_pawns(game.field, 'blue') == 0:
		game.winner = 'red'

	if game.winner != '':
		await alert_win(query)
		games.delete(game)
		return True


	return False

# изменяет текст и/или клавиатуру сообщения
async def rewrite(query: CallbackQuery):
	game = games.get(query.inline_message_id)

	text = f"""
***__The Castle Game {game.type}x{game.type}__***

***Игроки:***
    🔴 `{', '.join([plr.name for plr in game.teams['red']])}`
    🔵 `{', '.join([plr.name for plr in game.teams['blue']])}`

***Замки:***
    🏰: `{castle_pawns_count(game, 'red')}`
    🏯: `{castle_pawns_count(game, 'blue')}`

***Ходит:*** `{game.player_move.name}`
***Можно сделать {game.move} {'шаг' if game.move == 1 else 'шага'}***
	"""

	keyboard = copy(game.field)

	for y in range(9):
		for x in range(8):
			keyboard[y][x] = InlineKeyboardButton(f" {keyboard[y][x]} ", callback_data=f'{keyboard[y][x]}_{x}_{y}')

	markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

	await bot.edit_message_text(text, inline_message_id=query.inline_message_id, reply_markup=markup)

# выбор команды: красная/синяя
async def set_team(query: CallbackQuery, team):
	game = games.get(query.inline_message_id)
	if game is None:
		game = Game(query.inline_message_id)
		game.type = int(query.data.split(' ')[0])
		games.new(game)

	if team != 'again':
		if len(game.teams[team]) == game.type and not game.exist(team, query.from_user.id):
			await query.answer("Эта команда уже занята.")
			return
		
		if not game.exist(team, query.from_user.id):
			if game.exist(enemy(team), query.from_user.id):
				game.del_from(enemy(team), query.from_user.id)
			game.add_to(team, query.from_user.first_name, query.from_user.id)
		
		else:
			game.del_from(team, query.from_user.id)


	text = f"""
***__The Castle Game {game.type}x{game.type}__***

***Игроки:***
    🔴 `{', '.join([plr.name for plr in game.teams['red']])}`
    🔵 `{', '.join([plr.name for plr in game.teams['blue']])}`

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
	game = games.get(query.inline_message_id)

	if not game.full():
		await query.answer("Не все команды заполнены.")
		return
	
	game.team = game.next_team = rd.choice(['red', 'blue'])
	game.player_move = rd.choice(game.teams[game.team])
	game.move = rd.randint(1, 3)

	await rewrite(query)

# если пешка не выбрана(choosed_pawn), то будет выбрана
# но если пешка уже выбрана, будет возможность ею походить
async def pawn_move(query: CallbackQuery):
	game = games.get(query.inline_message_id)

	pawn_sym, x, y = query.data.split('_')
	x, y = int(x), int(y)


	if not game.exist(game.team, query.from_user.id):
		await query.answer("Сейчас ходит другой игрок.")
		return

	# выбор пешки
	if game.choosed is None:
		if pawn_sym in (['🏯', '🔹'] if game.team == 'red' else ['🏰', '🔺']):
			await query.answer("Этой пешкой нельзя ходить.")
			return
		elif pawn_sym == '.':
			await query.answer("Выберите пешку.")
			return

		game.choosed = query.data
		move = game.move

		game.append_moves([
			f"{catch(game, x, y+move)}_{x}_{y+move}",
			f"{catch(game, x+move, y+move)}_{x+move}_{y+move}",
			f"{catch(game, x+move, y)}_{x+move}_{y}",
			f"{catch(game, x+move, y-move)}_{x+move}_{y-move}",
			f"{catch(game, x, y-move)}_{x}_{y-move}",
			f"{catch(game, x-move, y-move)}_{x-move}_{y-move}",
			f"{catch(game, x-move, y)}_{x-move}_{y}",
			f"{catch(game, x-move, y+move)}_{x-move}_{y+move}"
		])

		del move

	# ход
	else:
		if pawn_sym in (['🔺', '🏰'] if game.team == 'red' else ['🔹', '🏯']):
			game.choosed = None
			game.moves.clear()
			await pawn_move(query)
			return

		if query.data not in game.moves:
			await query.answer("Сюда нельзя ходить.")
			return

		c_sym, c_x, c_y = game.choosed.split('_')
		c_x, c_y = int(c_x), int(c_y)

		if c_sym == ('🏰' if game.team == 'red' else '🏯'):
			if game.castle(game.team) == 0:
				await query.answer("В замке нету пешек для хода.")
				return


		if not (c_sym == ('🏰' if game.team == 'red' else '🏯')):
			game.field[c_y][c_x] = '.'

		game.field[y][x] = c_sym.replace('🏰', '🔺').replace('🏯', '🔹')

		if c_sym == ('🏰' if game.team == 'red' else '🏯'):
			game.dec(game.team)
		
		if pawn_sym == ('🔹' if game.team == 'red' else '🔺'):
			game.inc(enemy(game.team))

		elif pawn_sym == ('🏯' if game.team == 'red' else '🏰'):
			if game.team == 'red' and game.blue_castle == 0:
				game.blue_alive = False
			elif game.team == 'blue' and game.red_castle == 0:
				game.red_alive = False
			
			else:
				game.inc(game.team)
				game.dec(enemy(game.team))
					
				game.field[y][x] = '🏯' if game.team == 'red' else '🏰'

			if await check_win(query): return

		if await check_win(query): return


		game.choosed = None
		game.moves.clear()

		game.team = 'red' if game.team == 'blue' else 'blue'
		game.player_move = rd.choice(game.teams[game.team])
		game.move = rd.randint(1, 3)

		await rewrite(query)
