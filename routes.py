from flask import Blueprint, jsonify, abort, url_for
from chess.chess import ChessBoard as ChessBoardLibrary
from database import ChessGame as dbChessGame

blueprint = Blueprint("chess", __name__, url_prefix='/chess/')


@blueprint.route('<game_token>/', methods=['GET'])
def board():
    # current state of the chess board.
    pass


@blueprint.route('<game_token>/<start>/<end>/', methods=['POST'])
def move():
    # aborts if an invalid move. otherwise returns new board state after the move.
    pass


@blueprint.route('<game_token>/', methods=['GET'])
def players():
    # returns the current players for a game.
    pass


@blueprint.route('create/<your_password>/', methods=['POST'])
def create_game(your_password):
    game_json = ChessBoardLibrary().board
    game = dbChessGame.create(password1=your_password, board=game_json)
    token = game.id
    links = {}
    links['invite'] = url_for('chess.join_game', game_token=game.id, your_password='put_your_password_here')
    links['board'] = url_for('chess.board', game_token=game.id)
    links['move'] = url_for('chess.move', game_token=game.id,
                            start="start location: 'A2'", end="end location: 'B3'")
    data = dict(token=token, links=links)
    response = jsonify(data)
    response.status_code = 200
    return response


@blueprint.route('join/<game_token>/<your_password>/', methods=['POST'])
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
