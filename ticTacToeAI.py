# ticTacToeAI.py
# Rushy Panchal
# January 2014

import tk.ttkExtra as tk
import time
from tictactoe import *

PATH = "test_moves.dat"

def main():
	'''Main application process'''
	root = tk.Tk()
	tk.createBaseStyles(root)
	root.title("Tic Tac Toe AI")
	command_root = tk.Toplevel(root, resize = True)
	width, height = 3, 3
	board = Board(root, width, height, board_height = 400, board_width = 400, delay = 0)
	buttonFrame = tk.Frame(command_root)
	goOnceButton = tk.Button(buttonFrame, text = "Start Game", command = lambda: runGames(root, board, 1))
	goNButton = tk.Button(buttonFrame, text = "Run Repeated Games", command = lambda: runGames(root, board))
	clearButton = tk.Button(buttonFrame, text = "Clear Stats", command = lambda: reset(False, True))
	quitButton = tk.Button(buttonFrame, text = "Quit", command = root.close, style = "Quit.TButton")
	progress_bar = root.progress_bar = tk.Statusbar(command_root)
	games_left_var = root.games_left_var = tk.StringVar(command_root)
	games_left_var.set("Current Game: None")
	games_left_label = tk.Label(command_root, textvariable = games_left_var)
	time_var = root.time_var = tk.StringVar(command_root)
	time_var.set("Elapsed Time: 0s")
	wins_var = root.wins_var = tk.StringVar(command_root)
	wins_var.set("X Wins (AI): 0\nO Wins: 0\nTie: 0")
	wins_label = tk.Label(command_root, textvariable = wins_var)
	time_label = tk.Label(command_root, textvariable = time_var)
	beta = board.addAI(O, 'blue')
	alpha = board.addAI(X, 'red')
	alpha.startLearning(PATH, True) # toggle X's AI
	beta.startLearning(PATH, True) # toggle O's AI
	# alpha.startLearning()
	# beta.startLearning()
	goOnceButton.grid(row = 1, column = 1, padx = 5)
	goNButton.grid(row = 1, column = 2, padx = 5)
	# clearButton.grid(row = 2, column = 1, padx = 5, pady = 5)
	quitButton.grid(row = 2, column = 2, padx = 5, pady = 5)
	board.grid(row = 1, column = 1, pady = 5)
	games_left_label.grid(row = 1, pady = 5)
	progress_bar.grid(row = 2, pady = 5)
	time_label.grid(row = 3, pady = 5)
	wins_label.grid(row = 4, pady = 5)
	buttonFrame.grid(row = 5, pady = 5)
	root.center()
	command_root.focus()
	command_root.lift()
	command_root.center()
	root.mainloop()
	
def runGames(master, board, value = None):
	'''Run the game N number of times, where N is acquired from the user'''
	master.progress_bar.setValue(0)
	if not value:
		run_root = tk.Toplevel(master)
		window = tk.InputWindow(run_root, "How many games to run?", type = int, width = 200, from_ = 1, to = 10000)
		window.mainloop()
		value = window.get()
	start = time.time()
	for n in xrange(1, value + 1):
		board.startGame()
		master.progress_bar.setValue(100.0 * n / value)
		master.games_left_var.set("Current Game: {current} / {total}".format(current = n, total = value))
		master.time_var.set("Elapsed Time: {elapsed}s".format(elapsed = round(time.time() - start, 5)))
		master.wins_var.set("X Wins: {x}\nO Wins: {o}\nTie: {tie}".format(x = board.wins[X], o = board.wins[O], tie = board.wins[TIE]))
	master.progress_bar.setValue(100)
	
if __name__ == "__main__":
	main()
