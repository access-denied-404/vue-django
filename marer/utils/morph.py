from urllib.parse import quote

import requests


class MorpherApi:
    url = 'https://ws3.morpher.ru/russian/declension?s={}&format=json'

    @classmethod
    def get_response(cls, text, form=None):
        url = cls.url.format(quote(text))
        response = requests.get(url=url).json()
        return response if not form else response.get(form)