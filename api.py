#!flask/bin/python
from flask import Flask, jsonify, abort, request, Response, make_response, url_for

from chess.chess import ChessBoard as ChessBoardLibrary
from database import ChessGame as dbChessGame

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


@app.route('/create/<your_password>/', methods=['POST'])
def create_game(your_password):
    print("haven't made game yet")
    game = dbChessGame.create(password1=your_password)
    print("game is: ")
    print(game.to_obj())
    print("made game")
    token = game.id
    # invite_link = url_for('join_game')
    # print("made invite link")
    # move_link = url_for('move')
    # print("made move link")
    # board_link = url_for('board')
    # print("made board link")
    data = dict(token=token)  # , invite_link=invite_link, board=board_link, move=move_link)
    response = jsonify(data)
    response.status_code = 200
    return response


@app.route('/join/<game_token>/<your_password>/', methods=['POST'])
def join_game(game_token, your_password):
    # takes a game token and returns one. aborts if two players are already part of the game.
    game = dbChessGame.query.get(game_token)
    if game:
        if game.password1 and game.password2:
            abort(400, "Two players have already joined this game.")
        else:
            game.password2 = your_password
            game.save()
            # move_link = url_for('move')
            # board_link = url_for('board')
            data = dict(token=game.id)  # , board=board_link, move=move_link)
    else:
        abort(400, "That game doesn't exits.")

    response = jsonify(data)
    response.status_code = 200
    return response
