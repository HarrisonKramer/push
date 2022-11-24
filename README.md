# PUSH Card Game Simulator

## Introduction
This package provides a simple simulation environment for the card game [PUSH](https://boardgamegeek.com/boardgame/265256/push).

## Example
```python
from push.game import Player, Game

number_of_players = 5
players = [Player() for __ in range(number_of_players)]
game = Game(players)
winner = game.play()
```