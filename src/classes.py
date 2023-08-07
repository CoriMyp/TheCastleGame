class Player:
	def __init__(self, name, id):
		self.name = name
		self.id = id

class Game:
	def __init__(self, mid):
		self.mid = mid
		self.type = 1

		self.field = [
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

		self.teams = {
			'red': [],
			'blue': []
		}
		self.team = None
		self.player_move = None

		self.move = None
		self.moves = []
		self.choosed = None

		self.red_castle, self.blue_castle = (0, 0)
		self.red_alive, self.blue_alive = (True, True)

		self.winner = ''

	def player(self, team, pid) -> Player:
		for player in self.teams[team]:
			if player.id == pid:
				return player
			
		return Player("", 0)
			
	def exist(self, team, pid):
		for player in self.teams[team]:
			if player.id == pid:
				return True
		
		return False
			
	def t(self, pid):
		return 'red' if self.player('red', pid) else 'blue'
	
	def full(self):
		return set([len(self.teams['red']), len(self.teams['blue'])]) == set([self.type])
	
	def castle(self, team):
		if team == 'red':
			return self.red_castle
		elif team == 'blue':
			return self.blue_castle

	def append_moves(self, moves):
		self.moves += moves

	def add_to(self, team, name, pid):
		self.teams[team].append(Player(name, pid))

	def del_from(self, team, pid):
		self.teams[team].remove(self.player(team, pid))

	def inc(self, team):
		if team == 'red':
			self.red_castle += 1
		elif team == 'blue':
			self.blue_castle += 1

	def dec(self, team):
		if team == 'red':
			self.red_castle -= 1
		elif team == 'blue':
			self.blue_castle -= 1 		


class ActiveGames:
	def __init__(self):
		self.games = []
		
	def new(self, game: Game):
		self.games.append(game)
		
	def get(self, gid) -> Game:
		for game in self.games:
			if game.mid == gid:
				return game
			
	def delete(self, game: Game):
		self.games.remove(game)
