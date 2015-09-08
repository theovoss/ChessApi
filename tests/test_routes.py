import json


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
