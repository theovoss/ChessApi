import json

from .factories import ChessGameFactory


def load_response(response, key=None):
    """Load data (dict, list, etc.) from a Flask response object."""
    text = response.data.decode('utf-8')
    if text:
        print(text)
        data = json.loads(text)
        if key:
            return data[key]
        else:
            return data
    else:
        return None


class TestCreateGame:

    endpoint = "/chess/create/"

    def test_can_create_game(self, client, db):
        params = dict(password="hello")
        response = client.post(self.endpoint, data=json.dumps(params),
                               content_type='application/json')
        data = load_response(response)
        assert 'links' in data
        assert 'token' in data
        assert 'board' in data['links']
        assert 'move' in data['links']
        assert 'invite' in data['links']
        assert data['token'] in data['links']['move']
        assert data['token'] in data['links']['board']
        assert data['token'] in data['links']['invite']


class TestJoinGame:

    endpoint = "/chess/join/{}/"

    def test_can_join_a_game(self, client, db):
        game = ChessGameFactory()
        token = game.id

        params = dict(password="playa 2")
        response = client.post(self.endpoint.format(token), data=json.dumps(params),
                               content_type='application/json')
        data = load_response(response)

        assert response.status_code == 200
        assert data['token'] == game.id
        assert game.id in data['links']['board']
        assert game.id in data['links']['move']

    def test_cant_join_game_if_already_full(self, client, db):
        game = ChessGameFactory(password2="2nd player")
        token = game.id

        params = dict(password="playa 2")
        response = client.post(self.endpoint.format(token), data=json.dumps(params),
                               content_type='application/json')

        assert response.status_code == 400

    def test_cant_join_non_existent_game(self, client, db):
        token = "This is not a game"

        params = dict(password="playa 2")
        response = client.post(self.endpoint.format(token), data=json.dumps(params),
                               content_type='application/json')

        assert response.status_code == 400


class TestMakeAMove:

    endpoint = "/chess/move/{}/"

    def test_cant_make_a_move_if_the_game_doesnt_have_two_players(self, client, db):
        game = ChessGameFactory(password1="bob")
        token = game.id

        params = dict(password="bob", start="A2", end="A3")
        response = client.post(self.endpoint.format(token), data=json.dumps(params),
                               content_type='application/json')

        assert response.status_code == 400

    def test_cant_make_a_move_if_the_move_is_invalid(self, client, db):
        game = ChessGameFactory(password2="steve")
        token = game.id

        params = dict(password="bob", start="A1", end="A2")
        response = client.post(self.endpoint.format(token), data=json.dumps(params),
                               content_type='application/json')

        assert response.status_code == 400


class TestGetBoard:

    endpoint = "/chess/game/{}/"

    def test_can_get_starting_board_state(self, client, db):
        pass
