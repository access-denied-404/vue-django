from urllib.parse import quote

import requests


class MorpherApi:
    url = 'https://ws3.morpher.ru/russian/declension?s={}&format=json'

    @classmethod
    def get_response(cls, text, form=None):
        response_form = None
        try:
            url = cls.url.format(quote(text))
            response = requests.get(url=url).json()
            response_form = response if not form else response.get(form)
        except Exception:
            pass

        return response_form or '_' * len(text)
