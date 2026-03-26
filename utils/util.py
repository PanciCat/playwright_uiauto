# -*- coding: utf-8 -*-
# @Author   : pancicat
# @Time     : 2025/01/18
# @File     : util.py
# @Desc     : 公共工具函数（随机数据生成、AES 加密等）

import uuid

key_ori = 'qs7g4f1s6xsfv?9a'
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import binascii

import string
from faker import Faker

import random
import time


class genVariable():
    f = Faker(locale='zh_CN')

    def generate_name(self):
        return self.f.name()

    def generate_phone(self):
        return self.f.phone_number()

    def rad(self, a, b):
        return random.randint(int(a), int(b))

    def random_for_input(self):
        return "AUTOTEST_" + self.f.password(length=8, special_chars=True, digits=True, upper_case=True,
                                             lower_case=True)

    def generate_email(self):
        domain = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]
        username_length = random.randint(5, 10)

        username = ''.join(random.choices(string.ascii_lowercase, k=username_length))
        domain_name = random.choice(domain)
        email = username + "@" + domain_name

        return "AUTOTEST_" + email

    def take_key_value(self, name):
        return getattr(self, name)

    def now_date(self):
        return time.strftime('%Y-%m-%d', time.localtime(time.time()))

    @staticmethod
    def uuid_8():
        return str(uuid.uuid4()).split("-")[0]


def encryptForPassword(word, key_str=None):
    if key_str is None:
        key_str = key_ori
    key = key_str.encode('utf-8')

    if len(key) != 16:
        raise ValueError("Invalid AES key length. Key must be 16 bytes long.")

    cipher = AES.new(key, AES.MODE_ECB)
    padded_word = pad(word.encode('utf-8'), AES.block_size, style='pkcs7')
    encrypted = cipher.encrypt(padded_word)
    return encrypted


def encrypt_hex(word, key_str=None):
    encrypted = encryptForPassword(word, key_str)
    return binascii.hexlify(encrypted).decode('utf-8').upper()
