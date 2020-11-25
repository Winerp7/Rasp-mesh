import requests

URL = 'http://192.168.43.105:3000/pi/'

class Api:
    def __init__(self):
        self.id = '5f956e6dab148ff21ca3d084'

    def create_url(self, path):
        return URL + path

    def post_request(self, path, message):
        url = self.create_url(path)
        response = None
        try:
            response = requests.post(url, json=message, params={'id': self.id})
        except Exception as e:
            print(e)
        return response

    def get_request(self, path):
        url = self.create_url(path)
        response = None
        try:
            response = requests.get(url, params={'id': self.id})
        except Exception as e:
            print(e)
        return response