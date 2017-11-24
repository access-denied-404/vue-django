from OpenSSL.crypto import X509, FILETYPE_ASN1, load_certificate
from pyasn1.codec.der.decoder import decode
from pyasn1.codec.der.encoder import encode


def extract_certificate_from_sign(sign: str) -> X509:
    import base64
    old_sign_b64 = sign
    old_sign = base64.standard_b64decode(old_sign_b64)
    cert, rest = decode(old_sign)
    realcert = encode(cert[1][3])

    # remove the first DER identifier from the front
    realcert = realcert[2 + (realcert[1] & 0x7F) if realcert[1] & 0x80 > 1 else 2:]

    certificate = load_certificate(FILETYPE_ASN1, realcert)
    return certificate


def get_username_from_certificate(cert: X509) -> str:
    md5 = cert.digest('md5').decode('utf8')
    md5_arr = md5.split(':')
    ret_str_arr = []
    new_octet_size = 4
    idx = 0
    new_end = 0
    while new_end < len(md5_arr):
        new_start = idx * new_octet_size
        new_end = new_start + new_octet_size
        ret_str_arr.append(''.join(md5_arr[new_start:new_end]))
        idx += 1
    return ':'.join(ret_str_arr)
