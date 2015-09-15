from flask import Blueprint, jsonify, abort, url_for

from webargs import Arg
from webargs.flaskparser import FlaskParser

from chess.chess import Chess
from .database import ChessGame as dbChessGame

blueprint = Blueprint("chess", __name__, url_prefix='/chess/')
parser = FlaskParser(('query', 'json'))

move_args = {
    'start': Arg(str, required=True),
    'end': Arg(str, required=True),
    'password': Arg(str, required=True),
}

password_args = {
    'password': Arg(str, required=True)
}


@blueprint.route('<game_token>/', methods=['GET'])
def board(game_token):
    # current state of the chess board.
    db_game = dbChessGame.query.get(game_token)
    if db_game:
        game = Chess(existing_board=db_game.board)
        data = game.board.generate_fen()
        response = jsonify(data)
        response.status_code = 200
    else:
        abort(400, "That game doesn't exits.")
    return response


@blueprint.route('move/<game_token>/', methods=['POST'])
@parser.use_kwargs(move_args)
def move(game_token, start, end, password):
    # aborts if an invalid move. otherwise returns new board state after the move.
    game = dbChessGame.query.get(game_token)

    if game:
        if game.password1 is None or game.password2 is None:
            abort(400, "This game needs more players.")
        # valid game, check if valid move
        chess_game = Chess(game.board)
        chess_game.move(start, end)
    pass


@blueprint.route('<game_token>/', methods=['GET'])
def players(game_token):
    # returns the current players for a game.
    pass


@blueprint.route('create/', methods=['POST'])
@parser.use_kwargs(password_args)
def create_game(password):
    game_json = ChessBoardLibrary().board
    game = dbChessGame.create(password1=password, board=game_json)
    token = game.id
    links = {}
    links['invite'] = url_for('chess.join_game', game_token=game.id)
    links['board'] = url_for('chess.board', game_token=game.id)
    links['move'] = url_for('chess.move', game_token=game.id)
    data = dict(token=token, links=links)

    response = jsonify(data)
    response.status_code = 200
    return response


@blueprint.route('join/<game_token>/', methods=['POST'])
@parser.use_kwargs(password_args)
def join_game(game_token, password):
    # takes a game token and returns one. aborts if two players are already part of the game.
    game = dbChessGame.query.get(game_token)

    if game:
        if game.password1 and game.password2:
            abort(400, "Two players have already joined this game.")
        else:
            game.password2 = password
            game.save()
            links = {}
            links['board'] = url_for('chess.board', game_token=game.id)
            links['move'] = url_for('chess.move', game_token=game.id)
            data = dict(token=game.id, links=links)
    else:
        abort(400, "That game doesn't exits.")

    response = jsonify(data)
    response.status_code = 200
    return response
