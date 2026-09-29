# from odoo.addons.auth_ldap.models.res_users import Users
from odoo import fields, api, models, registry, SUPERUSER_ID
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
from odoo.http import request
import logging
import pytz
import json

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from base64 import b64encode
from Crypto.Random import get_random_bytes

import hashlib

_logger = logging.getLogger(__name__)


class Users(models.Model):
    _inherit = "res.users"

    data = fields.Char()

    @classmethod
    def _login(cls, db, login, password, user_agent_env):
        if not password:
            raise AccessDenied()
        ip = request.httprequest.environ['REMOTE_ADDR'] if request else 'n/a'
        try:
            with cls.pool.cursor() as cr:
                self = api.Environment(cr, SUPERUSER_ID, {})[cls._name]
                with self._assert_can_auth():
                    user = self.search(self._get_login_domain(login), order=self._get_login_order(), limit=1)
                    if not user:
                        raise AccessDenied()
                    user = user.with_user(user)
                    user._check_credentials(password, user_agent_env)
                    tz = request.httprequest.cookies.get('tz') if request else None
                    if tz in pytz.all_timezones and (not user.tz or not user.login_date):
                        # first login or missing tz -> set tz to browser tz
                        user.tz = tz
                    user._update_last_login()
                    user.get_encrypt_data(login, password, db)
        except AccessDenied:
            _logger.info("Login failed for db:%s login:%s from %s", db, login, ip)
            raise

        _logger.info("Login successful for db:%s login:%s from %s", db, login, ip)

        return user.id

    def encrypt_data(self, data, key):
        cipher = AES.new(key, AES.MODE_CBC)
        ciphertext = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
        iv = b64encode(cipher.iv).decode('utf-8')
        encrypted_data = b64encode(ciphertext).decode('utf-8')
        return f'{iv}:{encrypted_data}'

    def get_encrypt_data(self, login, passwd, db):
        #login = login.split('@')[0]
        data_to_encrypt = {'username': login, 'password': passwd, 'db': db}
        key = self.string_to_32byte('Bomba!Erp2024#')
        encrypted_data = self.encrypt_data(json.dumps(data_to_encrypt), key)
        self.sudo().update({
            'data': encrypted_data
        })
        return

    def string_to_32byte(self, input_string):
        # Using SHA-256 hash function
        sha256 = hashlib.sha256()
        sha256.update(input_string.encode('utf-8'))
        hash_result = sha256.digest()
        return hash_result

