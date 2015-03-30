# tictactoe.py
# Rushy Panchal
# January 2014

'''Holds the main game logistics for Tic Tac Toe, including AI handling'''

### Imports and global variables

import tk.ttkExtra as tk
import tk.graphics as graphics
import shutil
import random
import time
import os
import re

NONE = '-'
O = 'O'
X = 'X'
TIE = 'Tie'
GAME_END = ("Game", "End")
CANNOT_FIND = "Cannot Find Value"
RANDOM_MOVE = "Random Move"
CUR_DIR = os.getcwd()
MOVES_PATH = os.path.join(CUR_DIR, 'AI_moves.dat')
	
### Main classes

class Player(object):
	'''Main Player class'''
	def __init__(self, board, player, color):
		self.board, self.player, self.color = board, player, color
		self.positions = self.board.positions
		self.empty_positions = self.board.empty_positions
		
	def draw(self, x, y):
		'''Draws the representation of this player on the board'''
		if self.player == X:
			self.board.drawX(x, y, self.color)
		elif self.player == O:
			self.board.drawO(x, y, self.color)
		else:
			self.board.drawOther(self.player, x, y, self.color)
		
	def move(self):
		'''Asks the user for a move'''
		move_root = tk.Toplevel(self.board.master)
		move_app = PlayerMove(move_root, self.board)
		move_app.mainloop()
		choice = move_app.get()
		if choice == RANDOM_MOVE:
			return self.randomMove()
		else:
			return choice
		
	def randomMove(self):
		'''Makes a random move'''
		if not self.empty_positions:
			self.board.winner = self.board.checkWin()
			if not self.board.winner:
				self.board.winner = TIE
			return GAME_END
		else:
			x = random.choice(self.empty_positions.keys())
			y = random.choice(self.empty_positions[x].keys())
			self.movePiece(x, y)
			return x, y

	def movePiece(self, x, y):
		'''Moves to the (x, y) spot on the board'''
		del self.empty_positions[x][y]
		if len(self.empty_positions[x].keys()) == 0:
			del self.empty_positions[x]
		self.board.addPiece(self.player, x, y)
		self.draw(x, y)
		
	def gameEnd(self):
		'''Should be overriden in child classes'''
		pass
			
class AI(Player):
	'''Main AI class, that "learns" to play Tic Tac Toe'''
	def __init__(self, *args, **kwargs):
		self.moves_path = kwargs.get('moves_path', MOVES_PATH)
		try:
			del kwargs['moves_path']
		except KeyError:
			pass
		self.moves = ""
		self.learn = False
		self.shouldSave = False
		Player.__init__(self, *args, **kwargs)
	
	def move(self):
		'''Makes a move'''
		if not self.learn:
			return self.randomMove()
		move = self.bestMove()
		if move == CANNOT_FIND:
			self.shouldSave = True
			return self.randomMove()
		else:
			x, y = self.board.pointToCoordinate(move)
			try:
				self.movePiece(x, y)
			except KeyError:
				self.shouldSave = True
				x, y = self.randomMove()
			return (x, y)
		
	def bestMove(self):
		'''Finds the best possible move'''
		regex = self.board.player_order[0] + "," + self.board.moves_log + "((?:[0-9],?){0,})" + self.player
		pattern = re.compile(regex)
		moves = pattern.findall(self.moves)
		if not moves:
			return CANNOT_FIND
		else:
			moves = [i.split(',') for i in moves]
			return int(min(moves, key = len)[0])
		
	def startLearning(self, path = None, restart = False):
		'''Starts the AI's learning process'''
		self.learn = True
		if path:
			self.moves_path = path
		if not os.path.exists(self.moves_path):
			with open(self.moves_path, 'w') as moves_file:
				moves_file.write(self.moves)
		if not restart:
			with open(self.moves_path, 'r') as moves_file:
				self.moves = moves_file.read()
		else:
			self.moves = ""
				
	def stopLearning(self):
		'''Stops the AI's learning process'''
		self.learn = False
		self.saveMoves()
			
	def gameEnd(self):
		'''Updates the current log and finishes the game'''
		if self.learn:
			winner = self.board.winner
			if winner == TIE:
				winner = "T"
			self.moves += self.board.player_order[0] + "," + self.board.moves_log + winner +"\n"
			self.saveMoves()
			
	def saveMoves(self):
		'''Saves the learning process for the AI'''
		if self.learn and self.shouldSave:
			with open(self.moves_path, 'w') as moves_file:
				moves_file.write(self.moves)
			shutil.copyfile(self.moves_path, self.moves_path + "_backup")
	
class Board(tk.BaseCustomWidget):
	'''Main Board class, which handles the current positions and legal moves'''
	def __init__(self, master, width, height, **options):
		self.master, self.options = master, options
		self.width, self.height = width, height
		self.board_width = options.get('board_width', 400)
		self.board_height = options.get('board_height', 400)
		self.move_delay = options.get('delay', 0)
		self.shuffle_players = options.get('shuffle_players', True)
		self.players = {}
		self.wins = {TIE: 0}
		self.AIs = []
		self.moves_log = ""
		self.player_order = []
		self.last_move = (None, None)
		self.positions = {i: {j: NONE for j in xrange(1, self.height + 1)} for i in xrange(1, self.width + 1)}
		self.empty_positions = {x: {y: NONE for y in self.positions[x].keys() if self.positions[x][y] == NONE} for x in self.positions.keys()}
		self.winner = False
		self.text_size = int(float(self.board_width) / (4 * self.width))
		if self.text_size < 5:
			self.text_size = 5
		self.moves_left = self.total_moves = self.width * self.height
		self.createInterface()
		
	def createInterface(self):
		'''Creates the visual part of the board'''
		self.mainFrame = tk.Frame(self.master)
		self.winnerVar = tk.StringVar(self.mainFrame)
		self.winnerVar.set('Winner: None')
		self.winner_display = tk.Label(self.mainFrame, textvariable = self.winnerVar, font = ('Helvetica', 24))
		self.moves_left_var = tk.StringVar(self.mainFrame)
		self.moves_left_var.set('Open Spaces Left: {}'.format(self.moves_left))
		self.moves_display = tk.Label(self.mainFrame, textvariable = self.moves_left_var, font = ('Helvetiva', 16))
		self.moves_bar = tk.Statusbar(self.mainFrame)
		self.game_board = graphics.GraphWin(self.mainFrame, self.board_width, self.board_height, False)
		self.game_board.setCoords(0, self.height, self.width, 0)
		for x in xrange(1, self.width):
			line = graphics.Line(graphics.Point(x, 0), graphics.Point(x, self.height))
			line.draw(self.game_board)
		for y in xrange(1, self.height):
			line = graphics.Line(graphics.Point(0, y), graphics.Point(self.width, y))
			line.draw(self.game_board)
		self.pieces_drawn = []
		self.winner_display.grid(row = 1, pady = 5)
		self.moves_display.grid(row = 2, pady = 5)
		self.moves_bar.grid(row = 3, pady = 5)
		self.game_board.grid(row = 4, pady = 5)
		
	def addAI(self, id, color, *args, **kwargs):
		'''Adds an AI to the game'''
		player = AI(self, id, color, *args, **kwargs)
		self.AIs.append(player)
		self.players[id] = player
		self.wins[id] = 0
		return player
		
	def addPlayer(self, id, color, *args, **kwargs):
		'''Adds a player to the game'''
		player = Player(self, id, color, *args, **kwargs)
		self.players[id] = player
		self.wins[id] = 0
		return player
	
	def getFromID(self, id):
		'''Returns the piece from the id'''
		return self.players[id]
	
	def coordinateToPoint(self, x, y):
		'''Transforms the (x, y) board coordinate into a linear point'''
		return self.width * (y - 1) + x
	
	def pointToCoordinate(self, n):
		'''Transforms the linear point into an (x, y) board coordinate'''
		x = n % self.width
		y = n // self.width + 1
		if x == 0:
			x = self.width
			y -= 1
		return (x, y)
	
	def addPiece(self, id, x, y):
		'''Adds a piece to the position'''
		if self.positions[x][y] == NONE and not self.winner:
			self.positions[x][y] = id
			self.moves_left -= 1
			self.moves_left_var.set('Open Spaces Left: {}'.format(self.moves_left))
			win = self.checkWin()
			if win != NONE:
				self.winner = win
		elif not self.empty_positions:
			self.winner = TIE
			
	def occupiedBy(self, x, y):
		'''Returns who occupies the (x, y) position'''
		return self.positions[x][y]
			
	def columnOccupiedBy(self, x):
		'''Returns the occupations of the x column'''
		return [self.positions[x][y] for y in xrange(1, self.height + 1)]
			
	def rowOccupiedBy(self, y):
		'''Returns the occupations of the y row'''
		return [self.positions[x][y] for x in xrange(1, self.width + 1)]
			
	def diagonalOccupiedBy(self, x, y):
		'''Returns the occupations of the x, y diagonal'''
		if self.width != self.height: 
			return [NONE]
		if x == y:
			return [self.positions[pos][pos] for pos in xrange(1, self.width + 1)]
		elif (x, y) == (1, self.height):
			sub_from = self.width + 1
			return [self.positions[pos][sub_from - pos] for pos in xrange(1, self.width + 1)]
		else:
			return [NONE]
			
	def checkWin(self):
		'''Returns if either X or O has won, and returns a winner if there is one'''
		for row in xrange(1, self.height + 1):
			if len(set(self.rowOccupiedBy(row))) == 1:
				return self.occupiedBy(1, row)
		for column in xrange(1, self.width + 1):
			if len(set(self.columnOccupiedBy(column))) == 1:
				return self.occupiedBy(column, 1)
		for x, y in [(1, 1), (1, self.height)]:
			if len(set(self.diagonalOccupiedBy(x, y))) == 1:
				return self.occupiedBy(x, y)
		return False
	
	def setPlayerOrder(self, *players):
		'''Sets the order of the players'''
		self.player_order = players
	
	def drawX(self, x, y, color):
		'''Draws the X piece on the board at the (x, y) coordinate'''
		line_1 = graphics.Line(graphics.Point(x - 0.75, y - 0.75), graphics.Point(x - 0.25, y - 0.25))
		line_2 = graphics.Line(graphics.Point(x - 0.75, y - 0.25), graphics.Point(x - 0.25, y - 0.75))
		line_1.setOutline(color)
		line_2.setOutline(color)
		line_1.draw(self.game_board)
		line_2.draw(self.game_board)
		self.pieces_drawn.extend([line_1, line_2])
		self.game_board.update()
	
	def drawO(self, x, y, color):
		'''Draws the O piece on the board at the (x, y) coordinate'''
		piece = graphics.Circle(graphics.Point(x - 0.5, y - 0.5), 0.25)
		piece.setOutline(color)
		piece.draw(self.game_board)
		self.pieces_drawn.append(piece)
		self.game_board.update()
	
	def drawOther(self, id, x, y, color):
		'''Draws another piece-type on the board at the (x, y) coordinate'''
		piece = graphics.Text(graphics.Point(x - 0.5, y - 0.5), str(id)[:5])
		piece.setSize(self.text_size)
		piece.setTextColor(color)
		piece.draw(self.game_board)
		self.pieces_drawn.append(piece)
		self.game_board.update()
	
	def startGame(self):
		'''Starts the game'''
		self.reset()
		if not self.player_order:
			self.player_order = self.players.keys()
		if self.shuffle_players:
			random.shuffle(self.player_order)
		players = [self.getFromID(id) for id in self.player_order]
		while not self.winner:
			for player in players:
				x, y = player.move()
				if (x, y) == GAME_END:
					self.winner = TIE
					self.wins[TIE] += 1
					break
				self.moves_log += str(self.coordinateToPoint(x, y)) + ","
				if self.winner:
					self.wins[self.winner] += 1
					break
				self.moves_bar.setValue(100.0 * (self.total_moves - self.moves_left) / self.total_moves)
				time.sleep(self.move_delay)
		for player in players:
			player.gameEnd()
		self.winnerVar.set('Winner: {}'.format(self.winner))
		self.moves_bar.setValue(100)
		return self.winner
	
	def reset(self, removePlayers = False, resetStats = False):
		'''Resets the game'''
		if resetStats:
			self.wins[TIE] = 0
			for player in self.player.keys():
				self.wins[player] = 0
		if removePlayers:
			self.players = {}
		self.moves_log = ""
		self.moves_left = self.width * self.height
		graphics.undrawAll(*self.pieces_drawn)
		self.pieces_drawn = []
		for i in xrange(1, self.width + 1):
			self.positions[i] = {}
			self.empty_positions[i] = {}
			for j in xrange(1, self.height + 1):
				self.positions[i][j] = NONE
				self.empty_positions[i][j] = NONE
		self.winner = False
		self.winnerVar.set('Winner: None')

class PlayerMove(tk.BaseCustomWindow):
	'''Main class to acquire a player move'''
	def __init__(self, master, board):
		self.master, self.board = master, board
		# self.board.bind("<)
		
	def get(self):
		'''Returns the user choice'''
		return RANDOM_MOVE
