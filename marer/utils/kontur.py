import json
import logging

import requests
from django.conf import settings

logger = logging.getLogger('django')


def _api_request(method: str, **kwargs):
    api_key = settings.KONTUR_FOCUS_API_KEY

    get_addr = 'https://focus-api.kontur.ru/api3/{}?key={}'.format(method, api_key)
    kwargs_strings = ['&' + str(k) + '=' + kwargs[k] for k in kwargs]
    result = requests.get(get_addr + ''.join(kwargs_strings), )

    if 200 <= result.status_code < 300:
        logger.debug('Request finished successfully, status code: {}'.format(result.status_code))
        json_data = json.loads(result.text)
    else:
        logger.warning('Error in response, status code: {}'.format(result.status_code))
        json_data = {}

    logger.debug('Result data: ' + result.text)
    return json_data


def req(inn: str=None, ogrn: str=None):
    inn = inn or ''
    ogrn = ogrn or ''
    data = _api_request('req', inn=inn, ogrn=ogrn)
    return data[0] if len(data) == 1 else data


def analytics(inn: str=None, ogrn: str=None):
    inn = inn or ''
    ogrn = ogrn or ''
    data = _api_request('analytics', inn=inn, ogrn=ogrn)
    return data[0] if len(data) == 1 else data


def egrDetails(inn: str=None, ogrn: str=None):
    inn = inn or ''
    ogrn = ogrn or ''
    data = _api_request('egrDetails', inn=inn, ogrn=ogrn)
    return data[0] if len(data) == 1 else data


def companyAffiliatesReq(inn: str=None, ogrn: str=None):
    inn = inn or ''
    ogrn = ogrn or ''
    data = _api_request('companyAffiliates/req', inn=inn, ogrn=ogrn)
    return data


def beneficialOwners(inn: str=None, ogrn: str=None):
    inn = inn or ''
    ogrn = ogrn or ''
    data = _api_request('beneficialOwners', inn=inn, ogrn=ogrn)
    return data[0] if len(data) == 1 else data
