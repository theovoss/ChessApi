from flask import Blueprint, jsonify, abort, url_for, current_app, render_template, request
from flask.ext.login import login_required, current_user

from webargs import fields
from webargs.flaskparser import FlaskParser

from chess.chess import Chess
from .database import Game, User

blueprint = Blueprint("chess", __name__, url_prefix='/chess/')
parser = FlaskParser(('query', 'json'))

move_args = {
    'start': fields.Str(required=True),
    'end': fields.Str(required=True),
}

game_args = {
    'color': fields.Str(required=False, missing=None),
}

create_user_args = {
    'password': fields.Str(required=True),
    'email': fields.Str(required=True),
    'name': fields.Str()
}

def get_color(code):
    if code.isupper():
        return "white"
    return "black"

# lowercase = black, uppercase = white
piece_images = {
    'p': 'https://upload.wikimedia.org/wikipedia/commons/c/cd/Chess_pdt60.png',
    'P': 'https://upload.wikimedia.org/wikipedia/commons/0/04/Chess_plt60.png',
    'q': 'https://upload.wikimedia.org/wikipedia/commons/a/af/Chess_qdt60.png',
    'Q': 'https://upload.wikimedia.org/wikipedia/commons/4/49/Chess_qlt60.png',
    'k': 'https://upload.wikimedia.org/wikipedia/commons/e/e3/Chess_kdt60.png',
    'K': 'https://upload.wikimedia.org/wikipedia/commons/3/3b/Chess_klt60.png',
    'n': 'https://upload.wikimedia.org/wikipedia/commons/f/f1/Chess_ndt60.png',
    'N': 'https://upload.wikimedia.org/wikipedia/commons/2/28/Chess_nlt60.png',
    'r': 'https://upload.wikimedia.org/wikipedia/commons/a/a0/Chess_rdt60.png',
    'R': 'https://upload.wikimedia.org/wikipedia/commons/5/5c/Chess_rlt60.png',
    'b': 'https://upload.wikimedia.org/wikipedia/commons/8/81/Chess_bdt60.png',
    'B': 'https://upload.wikimedia.org/wikipedia/commons/9/9b/Chess_blt60.png'
}


def load_url_map(app):
    url_map = {}
    for rule in app.url_map.iter_rules():
        url_format = rule.rule.replace("<", "%7B").replace(">", "%7D").replace("path:", "")
        args = [arg.replace("{", "%7B").replace("}", "%7D") for arg in rule.arguments]
        url_map[rule.endpoint] = dict(url=url_format,
                                      arguments=args)

    return url_map


@blueprint.route('', methods=['GET'])
def root():
    routes = load_url_map(current_app)
    print(routes)
    response = jsonify(routes)
    import pdb
    pdb.set_trace()
    response.status_code = 200
    return response


@blueprint.route('game/<game_token>/selected/<row>/<column>/', methods=['GET'])
def selected(game_token, row, column):
    db_game = Game.query.get(game_token)
    if not db_game:
        abort(400, "That game doesn't exits.")
    board = db_game.board
    game = Chess(existing_board=board)
    index = (int(row), int(column))
    destinations = game.destinations(index)
    return render_template('selected.html', rows=8, columns=8, board=board, images=piece_images, destinations=destinations)



@blueprint.route('game/<game_token>/', methods=['GET'])
def board(game_token):
    db_game = Game.query.all()[0]
    c = Chess(existing_board=db_game.board)
    destinations = []
    if request.args:
        game = Chess(existing_board=db_game.board)
        input_id = min([k for k in request.args])
        input_piece = request.args[input_id]
        row, col = input_id.split('.')
        index = (int(row), int(col))
        destinations = game.destinations(index)
        if destinations:
            return redirect(url_for('selected'))

        # print("Pressed row: {} col: {}".format(row, col))
        # print("Piece is a: {}".format(get_color(input_piece) + " " + input_piece))
    # current state of the chess board.
    # db_game = Game.query.get(game_token)
    if db_game:
        # game = Chess(existing_board=db_game.board)
        # data = game.generate_fen()
        # render_template('board.html', rows=game._board.rows, columns=game._board.columns, board=game.board)
        return render_template('board.html', rows=8, columns=8, board=db_game.piece_locations, images=piece_images)
    else:
        abort(400, "That game doesn't exits.")


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


@blueprint.route('create-user/', methods=['POST'])
@parser.use_kwargs(create_user_args)
def create_user(email, password, name):
    user = User.query.filter_by(email=email).first()
    if user:
        abort(400, "A user with that email already exist.")

    User.create(email=email, password=password, name=name)
    data = dict(success="yep")
    response = jsonify(data)
    response.status_code = 200
    return response


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
