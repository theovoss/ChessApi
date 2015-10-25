import json
import base64


class AuthorizedClient:

    def __init__(self, app, email, password):
        self.client = app.test_client()
        self.email = email
        self.password = password
        self.auth_header_value = self.generate_basic_auth_header()

    def generate_basic_auth_header(self):
        combined = "{}:{}".format(self.email, self.password)
        bytes_combined = combined.encode('utf-8')
        encoded = base64.b64encode(bytes_combined)
        return encoded

    def get_auth_header(self):
        return dict(Authorization=b"".join([b"Basic ", self.auth_header_value]))

    def post(self, endpoint, data=None, content_type='application/json', **kwargs):
        auth_header = self.get_auth_header()
        kwargs['headers'] = auth_header

        if content_type == 'application/json':
            data = json.dumps(data)

        return self.client.post(endpoint, data=data, content_type=content_type, **kwargs)

    def patch(self, endpoint, data=None, content_type='application/json', **kwargs):
        auth_header = self.get_auth_header()
        kwargs['headers'] = auth_header

        if content_type == 'application/json':
            data = json.dumps(data)

        return self.client.patch(endpoint, data=data, content_type=content_type, **kwargs)

    def get(self, endpoint, data=None, content_type='application/json', **kwargs):
        auth_header = self.get_auth_header()
        kwargs['headers'] = auth_header

        if content_type == 'application/json':
            data = json.dumps(data)

        return self.client.get(endpoint, data=data, content_type=content_type, **kwargs)

    def delete(self, endpoint, data=None, content_type='application/json', **kwargs):
        auth_header = self.get_auth_header()
        kwargs['headers'] = auth_header

        if content_type == 'application/json':
            data = json.dumps(data)

        return self.client.delete(endpoint, data=data, content_type=content_type, **kwargs)
