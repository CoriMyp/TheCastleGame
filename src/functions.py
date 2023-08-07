# функция подсчитывает кол-во пешек данной команды
def count_pawns(field, team):
	sym = '🔺' if team == 'red' else '🔹'
	field_arr = []

	for raw in field:
		for pawn in raw:
			field_arr.append(pawn)

	return field_arr.count(sym)

# функция ловит возможную ошибку, служит для уменьшения и читаемости кода	
def catch(game, x, y):
	try:
		return game.field[y][x]
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
def castle_pawns_count(game, team):
	if team == 'red' and game.red_alive:
		return f'{game.red_castle} {string_num(game.red_castle)}'
	elif team == 'blue' and game.blue_alive:
		return f'{game.blue_castle} {string_num(game.blue_castle)}'
	else:
		return 'замок разрушен'