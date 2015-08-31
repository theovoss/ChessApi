#!flask/bin/python
from flask import Flask, jsonify, abort, request, Response, make_response, url_for

from chess import ChessBoard

app = Flask(__name__, static_url_path="")


@app.route('/<game_token>/', methods=['GET'])
def board():
    # current state of the chess board.
    pass


@app.route('/<game_token>/<start>/<end>/', methods=['POST'])
def move():
    # aborts if an invalid move. otherwise returns new board state after the move.
    pass


@app.route('/<game_token>/', methods=['GET'])
def players():
    # returns the current players for a game.
    pass


@app.route('/create/', methods=['POST'])
def create_game():
    # returns a game token specific to the player
    pass


@app.route('/<game_token>/', methods=['POST'])
def join_game():
    # takes a game token and returns one. aborts if two players are already part of the game.
    pass
