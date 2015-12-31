from flask import Blueprint, jsonify, abort, url_for
from flask.ext.login import login_required, current_user

from webargs import fields
from webargs.flaskparser import FlaskParser

from chess.chess import Chess
from .database import Game as Game

blueprint = Blueprint("chess", __name__, url_prefix='/chess/')
parser = FlaskParser(('query', 'json'))

move_args = {
    'start': fields.Str(required=True),
    'end': fields.Str(required=True),
}

game_args = {
    'color': fields.Str(required=False, missing=None),
}


@blueprint.route('game/<game_token>/', methods=['GET'])
def board(game_token):
    # current state of the chess board.
    db_game = Game.query.get(game_token)

    if db_game:
        game = Chess(existing_board=db_game.board)
        data = game.generate_fen()
        players = []

        for player in db_game.players:
            players.append(player.name)

        response = jsonify(dict(board=data, players=players))
        response.status_code = 200
    else:
        abort(400, "That game doesn't exits.")

    return response


@blueprint.route('move/<game_token>/', methods=['POST'])
@parser.use_kwargs(move_args)
@login_required
def move(game_token, start, end):
    # aborts if an invalid move. otherwise returns new board state after the move.
    game = Game.query.get(game_token)

    if game:
        if not game.is_full:
            abort(400, "This game needs more players.")

        chess = Chess(game.board)

        for player in game.board['players']:
            if game.current_player != current_user:
                abort(400, "Not your turn cheater!")
        # valid game, check if valid move
        success = chess.move(start, end)

        if not success:
            abort(400, "Moving from {} to {} is an invalid move.".format(start, end))

        data = dict(token=game.id, board=chess.generate_fen())
        response = jsonify(data)
        response.status_code = 200
        return response
    else:
        abort(400, "The game does not exist.")


@blueprint.route('<game_token>/', methods=['GET'])
def players(game_token):
    # returns the current players for a game.
    pass


@blueprint.route('create/', methods=['POST'])
@parser.use_kwargs(game_args)
@login_required
def create_game(color="white"):
    game_json = Chess().export()

    game = Game.create(board=game_json, player_1=current_user)
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
@parser.use_kwargs(game_args)
@login_required
def join_game(game_token, color="black"):
    # takes a game token and returns one. aborts if two players are already part of the game.
    game = Game.query.get(game_token)

    if game:
        if len(game.players) == len(game.board['players']):
            abort(400, "All players have already joined this game.")
        else:
            game_json = game.board
            colors = ["black", None] if game.player_2 is None else []

            if color not in colors:
                abort(400, "The color {} is not available.".format(color))
            game.board = game_json
            game.players.append(current_user)
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
