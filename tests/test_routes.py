import json
import pytest

from .factories import GameFactory, UserFactory
from .utilities import generate_uuid

starting_fen_configuration = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


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


class TestAuthentication:

    endpoint_create = "/chess/create/"
    endpoint_join = "/chess/join/{}/"

    def test_cant_create_game_without_credentials(self, client, db):
        response = client.post(self.endpoint_create)

        assert response.status_code == 401

    def test_cant_join_game_without_credentials(self, client, db):
        game = GameFactory()
        response = client.post(self.endpoint_join.format(game.id))

        assert response.status_code == 401

    def test_can_create_game_when_logged_in(self, authorized_client, db):
        response = authorized_client.post(self.endpoint_create)

        assert response.status_code == 200

    def test_can_join_game_when_logged_in(self, authorized_client, db):
        game = GameFactory()
        response = authorized_client.post(self.endpoint_join.format(game.id))

        assert response.status_code == 200


class TestCreateGame:

    endpoint = "/chess/create/"

    def test_can_create_game(self, authorized_client, db):
        response = authorized_client.post(self.endpoint)
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

    def test_can_join_a_game(self, authorized_client, db):
        game = GameFactory()
        token = str(game.id)

        response = authorized_client.post(self.endpoint.format(token))
        data = load_response(response)

        assert response.status_code == 200
        assert data['token'] == token
        assert token in data['links']['board']
        assert token in data['links']['move']

    def test_cant_join_game_if_already_full(self, authorized_client, db):
        game = GameFactory()
        game.players.append(UserFactory())
        game.players.append(UserFactory())
        game.save()

        token = game.id

        response = authorized_client.post(self.endpoint.format(token))

        assert response.status_code == 400

    def test_cant_join_non_existent_game(self, authorized_client, db):
        token = generate_uuid()

        response = authorized_client.post(self.endpoint.format(token))

        assert response.status_code == 400


class TestMakeAMove:

    endpoint = "/chess/move/{}/"

    def test_cant_make_a_move_if_the_game_doesnt_have_two_players(self, authorized_client, db):
        game = GameFactory(players=[authorized_client.user])
        token = game.id

        params = dict(start="A2", end="A3")
        response = authorized_client.post(self.endpoint.format(token), data=params)

        assert response.status_code == 400

    def test_cant_make_a_move_if_the_move_is_invalid(self, authorized_client, db):
        game = GameFactory(players=[authorized_client.user, UserFactory()])
        token = game.id

        params = dict(start="A1", end="A2")
        response = authorized_client.post(self.endpoint.format(token), data=params)

        assert response.status_code == 400

    def test_can_make_a_valid_move(self, authorized_client, db):
        game = GameFactory(players=[authorized_client.user, UserFactory()])
        token = game.id

        params = dict(start="A2", end="A3")
        response = authorized_client.post(self.endpoint.format(token), data=params)

        assert response.status_code == 200

        data = load_response(response)

        assert data['board'].split('/')[5][0] == 'P'


class TestGetBoard:

    endpoint = "/chess/game/{}/"

    def test_can_get_starting_board_state(self, authorized_client, db):
        game = GameFactory(players=[authorized_client.user, UserFactory()])
        token = game.id

        response = authorized_client.get(self.endpoint.format(token))

        data = load_response(response)

        assert data['board'] == starting_fen_configuration

    def test_can_get_all_users_games(self, authorized_client, db):
        game = GameFactory()
        user1 = UserFactory()
        user2 = UserFactory()
        game.players.append(user1)
        game.players.append(user2)

        response = authorized_client.get(self.endpoint.format(str(game.id)))

        data = load_response(response)

        assert user1.name in data['players']
        assert user2.name in data['players']
