import json
import base64
import time
from collections import namedtuple
from enum import IntEnum
from urllib import request
from cryptography.hazmat.primitives import padding, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

_SERVER_PUBLIC_KEY = '04c5c00c4f8d1197cc7c3167c52bf7acb054d722f0ef08dcd7e0883236e0d72a3868d9750cb47fa4619248f3d83f0f662671dadc6e2d31c2f41db0161651c7c076'

ApiResult = namedtuple("ApiResult", ["success", "data", "code", "msg"])


class ReturnCode(IntEnum):
    SUCCESS = 0
    INVALID_LOGIN = 26006
    CAPTCHA_REQUIRED = 100032

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, int):
            return cls._create_pseudo_member_(value)
        return None

    @classmethod
    def _create_pseudo_member_(cls, value):
        pseudo_member = cls._value2member_map_.get(value, None)
        if pseudo_member is None:
            new_member = int.__new__(cls, value)
            new_member._name_ = str(value)
            new_member._value_ = value
            pseudo_member = cls._value2member_map_.setdefault(value, new_member)
        return pseudo_member


class Client:

    def __init__(self, email=None, password=None, region=None, login_response_data=None):
        """

        :param email:
        :param password:
        :param region:
        :param login_response_data:
        """
        self.email = email
        self.password = password
        self.region = region
        self.login_response_data = login_response_data
        if login_response_data is None:
            self.user_id = None
            self.auth_token = None
            self.token_expires_at = None
            self.nick_name = None
            self.invitation_code = None
            self.geo_key = None
            self.server_public_key = None
        else:
            self.user_id = login_response_data['user_id']
            self.auth_token = login_response_data['auth_token']
            self.token_expires_at = login_response_data['token_expires_at']
            self.nick_name = login_response_data['nick_name']
            self.invitation_code = login_response_data['invitation_code']
            self.geo_key = login_response_data['geo_key']
            self.server_public_key = login_response_data['server_secret_info']['public_key']

    def login(self, captcha_id="", answer="") -> ApiResult:
        """Attempt to login to AnkerMake cloud service

        Upon a successful login, the returned ApiResult.data should be retained and passed into future Client()
        initializations in order to skip the login process as long as the token is still valid.

        :param captcha_id: when login fails with CAPTCHA_REQUIRED, this is the id of the captcha
        :param answer: answer to the captcha
        :return:
        :rtype: ApiResult
        """
        try:
            pubkey = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), bytes.fromhex(_SERVER_PUBLIC_KEY))

            client_key_pair = ec.generate_private_key(ec.SECP256R1())
            client_public_key = client_key_pair.public_key().public_bytes(serialization.Encoding.X962,
                                                                          serialization.PublicFormat.UncompressedPoint).hex()

            shared_key = client_key_pair.exchange(ec.ECDH(), pubkey)

            iv = shared_key[0:16]
            padder = padding.PKCS7(256).padder()
            padded_data = padder.update(self.password.encode()) + padder.finalize()
            cipher = Cipher(algorithms.AES(shared_key), modes.CBC(iv))
            encryptor = cipher.encryptor()
            encrypted_password = encryptor.update(padded_data) + encryptor.finalize()

            data = dict(
                ab=self.region,
                answer=answer,
                captcha_id=captcha_id,
                client_secret_info=dict(
                    public_key=client_public_key
                ),
                email=self.email,
                login_id="",
                password=base64.b64encode(encrypted_password).decode('utf-8'),
                time_zone=time.localtime().tm_gmtoff,
                verify_code=""
            )

            req = request.Request('https://make-app.ankermake.com/v2/passport/login',
                                  data=json.dumps(data).encode('utf-8'))
            self._add_request_headers(req, False)
            req.add_header('content-type', 'application/json')
            response = request.urlopen(req)

            if response.status == 200:
                response_data = json.loads(response.read().decode('utf-8'))
                if response_data['code'] == 0:
                    self.user_id = response_data['data']['user_id']
                    self.auth_token = response_data['data']['auth_token']
                    self.token_expires_at = response_data['data']['token_expires_at']
                    self.nick_name = response_data['data']['nick_name']
                    self.invitation_code = response_data['data']['invitation_code']
                    self.geo_key = response_data['data']['geo_key']
                    self.server_public_key = response_data['data']['server_secret_info']['public_key']
                return ApiResult(['code'] == 0, response_data['data'], response_data['code'], response_data['msg'])
            else:
                print("AnkerMake Client login: Non 200 response from server: " + str(response.status))
                print("Response data: " + response.read())

        except Exception as e:
            print("AnkerMake Client login: Error connecting to server: " + str(e))

        return ApiResult(False, None, None, None)

    def get_fdm_list(self) -> ApiResult:
        """

        :rtype: ApiResult
        """
        try:
            req_data = dict(
                device_sn="",
                num=100,
                orderby="",
                page=0,
                station_sn="",
                time_zone=time.localtime().tm_gmtoff
            )
            req = request.Request('https://make-app.ankermake.com/v1/app/query_fdm_list',
                                  data=json.dumps(req_data).encode('utf-8'))
            self._add_request_headers(req)
            req.add_header('content-type', 'application/json')

            response = request.urlopen(req)
            if response.status == 200:
                response_data = json.loads(response.read().decode('utf-8'))
                return ApiResult(response_data['code'] == 0, response_data['data'], response_data['code'],
                                 response_data['msg'])

        except Exception as e:
            print("AnkerMake Client getFDMList: Error fetching FDM printer list: " + str(e))

        return ApiResult(False, None, None, None)

    def _add_request_headers(self, req, include_auth_token=True):
        req.add_header('Model_type', 'PC')
        req.add_header('User-Agent', 'Mozilla/5.0')
        req.add_header('app_name', 'anker_make')
        req.add_header('timeoffset', str(time.localtime().tm_gmtoff))
        req.add_header('timezone', time.localtime().tm_zone)
        if include_auth_token:
            req.add_header('x-auth-token', self.auth_token)
