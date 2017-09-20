"""
All functions and classes described here are stubs.
All of it must be re-declared and re-implemented somewhere else.
"""
from marer.models import Issuer


def create_stub_issuer(user_owner, issuer_name):
    issuer = Issuer(
        full_name=issuer_name,
        short_name=issuer_name,
        inn='0000000000',
        kpp='000000000',
        ogrn='0000000000000',
        user=user_owner.user,
    )
    issuer.save()
    return issuer

