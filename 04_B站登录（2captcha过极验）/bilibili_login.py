import random
import requests
import base64
import json
import time
from pprint import pprint
from http import cookiejar
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
import warnings
warnings.filterwarnings("ignore")


class Bilibili_Account(object):
    def __init__(self, username: str = None, password: str = None):
        self.username = username
        self.password = password

        # api_key 在2captcha 网站注册后获取，需要付费使用
        self.api_key = ''

        self.login_data = {
            'username': '',
            'password': '',
            'captchaType': '6',
            'keep': 'true',
            'goUrl': 'https://www.bilibili.com/',
            }
        self.session = requests.session()
        self.session.cookies = cookiejar.LWPCookieJar(filename='./cookies.txt')


    def login(self, load_cookies=True):
        """
        模拟登录B站
        :param load_cookies: 是否读取上次保存的 Cookies
        :return: bool
        """
        if load_cookies and self.load_cookies():
            print('读取 Cookies 文件')
            if self.check_login():
                print('登录成功')
                return True
            print('Cookies 已过期')

        self._check_user_pass()
        self.login_data.update({'username': self.username})

        # 获取gt、challenge、key
        r = self._get_challenge()
        self.login_data.update({'key': r['data']['result']['key']})

        # 获取validate
        r = self._get_validate(r)
        self.login_data.update({
            'challenge': r["geetest_challenge"],
            'validate': r["geetest_validate"],
            'seccode': r["geetest_seccode"]
            })

        # 密码加密
        password = self._encrypt(self.password)
        self.login_data.update({
            'password': password
            })

        # 登录
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36',
            'content-type': 'application/x-www-form-urlencoded',
            'referer': 'https://passport.bilibili.com/login',
            }
        r = self.session.post('https://passport.bilibili.com/web/login/v2', data=self.login_data, headers=headers)
        # print('\033[1;31m登录状态：\033[0m \n', r.text)

        if 'massage' in r.text:
            print(r.json()['message'])
        if self.check_login():
            print('登录成功')
            return True
        print('登录失败')
        return False


    def load_cookies(self):
        """
        读取 Cookies 文件加载到 Session
        :return: bool
        """
        try:
            self.session.cookies.load(ignore_discard=True)
            return True
        except FileNotFoundError:
            return False

    def check_login(self):
        """
        检查登录状态，访问登录页面出现跳转则是已登录，
        如登录成功保存当前 Cookies
        :return: bool
        """
        r = requests.get('http://api.bilibili.com/nav', cookies=self.session.cookies)
        if r.json()['code'] == 0:
            self.session.cookies.save()
            return True
        return False

    def _check_user_pass(self):
        """
        检查用户名和密码是否已输入，若无则手动输入
        """
        if not self.username:
            self.username = input('请输入手机号：')

        if not self.password:
            self.password = input('请输入密码：')

    def _get_challenge(self):
        """
        获取gt、challenge、key
        """
        r = self.session.get('https://passport.bilibili.com/web/captcha/combine?plat=6')
        pprint(r.json())
        return r.json()

    def _get_validate(self, r):
        payload = {
            'key': self.api_key,
            'method': 'geetest',
            'gt': r['data']['result']['gt'],
            'challenge': r['data']['result']['challenge'],
            'api_server': 'api.geetest.com',
            'pageurl': 'https://passport.bilibili.com/login',
            'json': '1'
            }
        r = self.session.get('https://2captcha.com/in.php', params=payload, verify=False)
        print('\033[1;31m获取2captcha的request-id：\033[0m')
        pprint(r.json())

        print('\033[1;31m等待2captcha返回validate......\033[0m')
        time.sleep(30)

        payload = {
            'key': self.api_key,
            'action': 'get',
            'id': r.json()['request']
            }

        while True:
            r = self.session.get('https://2captcha.com/res.php', params=payload)
            if r.text[:2] == 'OK':
                r_json = json.loads(r.text[3:])
                pprint(r_json)
                return r_json
            else:
                print(r.text)
                time.sleep(5)

    def _encrypt(self, password):
        r = self.session.get('https://passport.bilibili.com/login?act=getkey&r={}'.format(random.random()))
        print('\033[1;31m获取公钥：\033[0m')
        pprint(r.json())
        key, _hash = r.json()['key'], r.json()['hash']
        rsakey = RSA.importKey(key)
        cipher = Cipher_pkcs1_v1_5.new(rsakey)  
        encrypted_password = base64.b64encode(cipher.encrypt((_hash + password).encode("utf-8"))).decode('utf8') 
        return encrypted_password




if __name__ == '__main__':
    account = Bilibili_Account('', '')
    account.login(load_cookies=True)