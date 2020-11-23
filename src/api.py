URL = 'http://192.168.43.105:3000/pi/'

class Api:
    def __init__(self):
        pass

    def create_url(self, path):
        return URL + path 

    def post_request(self, path, message):
        url = self.create_url(path)
        response = None
        try:
            response = requests.post(url, json=message)
        except Exception as e:
            print(e)
        return response

    def get_request(self, path, message):
        url = self.create_url(path)
        response = None
        try:
            response = requests.get(url, json=message)
        except Exception as e:
            print(e)
        return response