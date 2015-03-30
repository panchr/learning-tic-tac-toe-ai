# learning-tic-tac-toe-ai
## A minimalist, learning Tic-Tac-Toe AI written in Python

This project is my first attempt to create a learning game AI.
However, instead of using classical Machine Learning algorithms, it utilizes reinforcement learning.

The AI initially uses just random moves. However, it records every game played, with data on who started and who won.
Then, it searches for the current game in that data. If a match is not found, then it plays randomly.
Otherwise, it executes the next move in the given sequence.

Currently, playing against the AI is not supported. Instead, it just plays against itself.
