import re
import time
import qrcode
import requests


class zjuamPC:
    """
    PC端登录浙大通行证
    """
    def __init__(self, username, password):
        """
        初始化
        :param username: 用户名（学号）
        :param password: 密码
        """
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:84.0) Gecko/20100101 Firefox/84.0',
        }
        self.login_url = 'https://zjuam.zju.edu.cn/cas/login'
        self.pubkey_url = 'https://zjuam.zju.edu.cn/cas/v2/getPubKey'

    def login(self):
        """
        登录函数
        :return: session
        """
        # 获取公钥
        pubkey = self.session.get(self.pubkey_url).json()
        exponent, modulus = pubkey['exponent'], pubkey['modulus']

        data = {
            'username': self.username,
            'password': self._rsa_encrypt(self.password, exponent, modulus),
            'execution': self._get_execution(),
            'authcode': '',
            '_eventId': 'submit'
        }
        resp = self.session.post(self.login_url, data=data)

        # 登录成功，获取姓名
        if self.check_login():
            print(re.search('nick: \'(.*?)\'', resp.text).group(1), '登录成功!')
            return self.session
        else:
            print('登录失败。')
            return

    def _rsa_encrypt(self, password, exponent, modulus):
        """
        RSA加密函数
        :param password: 原始密码
        :param exponent: 十六进制exponent
        :param modulus: 十六进制modulus
        :return: RSA加密后的密码
        """
        password_bytes = bytes(password, 'ascii')
        password_int = int.from_bytes(password_bytes, 'big')
        e_int = int(exponent, 16)
        m_int = int(modulus, 16)
        result_int = pow(password_int, e_int, m_int)
        return hex(result_int)[2:].rjust(128, '0')

    def _get_execution(self):
        """
        从页面HTML中获取execution的值
        :return: execution的值
        """
        resp = self.session.get(self.login_url)
        return re.search('name="execution" value="(.*?)"', resp.text).group(1)

    def check_login(self):
        """
        检查登录状态，访问登录页面出现跳转则是已登录，
        :return: bool
        """
        resp = self.session.get(self.login_url, allow_redirects=False)
        if resp.status_code == 302:
            return True
        return False


class zjuamScanqr:
    """
    钉钉扫描二维码登录浙大通行证
    """
    def __init__(self):
        """
        初始化，主要是各种url
        """
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:84.0) Gecko/20100101 Firefox/84.0',
        }
        self.qrcode_url = 'https://login.dingtalk.com/user/qrcode/generate?bizScene=http_third_party&sceneId=dingoayiy2etqcpmyc0lpk'
        self.qrcode_image_url = 'https://oapi.dingtalk.com/connect/qrcommit?showmenu=false&code={}&appid=dingoayiy2etqcpmyc0lpk&redirect_uri=https%3A%2F%2Fzjuam.zju.edu.cn%2Fcas%2Flogin%3Fclient_name%3DDingDingClient'
        self.um_url = 'https://ynuf.alipay.com/service/um.json'
        self.login_url = 'https://login.dingtalk.com/login/login_with_qr'
        self.main_page_url = 'https://zjuam.zju.edu.cn/cas/login'

    def login(self):
        """
        登录函数
        :return: session
        """
        # 获取二维码
        resp = self.session.get(self.qrcode_url)
        qr_code = resp.json()['result']
        qr_img = qrcode.make(self.qrcode_image_url.format(qr_code)).resize((300, 300))
        qr_img.show()

        # 循环检测二维码扫描情况
        while True:
            data = {
                'qrCode': qr_code,
                'goto': 'https://oapi.dingtalk.com/connect/oauth2/sns_authorize?appid=dingoayiy2etqcpmyc0lpk&response_type=code&scope=snsapi_login&state=STATE&redirect_uri=https%3A%2F%2Fzjuam.zju.edu.cn%2Fcas%2Flogin%3Fclient_name%3DDingDingClient',
                'pdmToken': self.session.post(self.um_url, data={'data': ''}).json()['id'],
                'bizScene': 'http_third_party',
                'sceneId': 'dingoayiy2etqcpmyc0lpk'
            }
            resp = self.session.post(self.login_url, data=data)
            resp_json = resp.json()

            # 扫码成功
            if resp_json['success']:
                self.session.get(resp_json['data'])
                break
            # 扫码中
            elif resp_json['code'] in ['11021', '11041']:
                pass
            # 二维码过期或其他情况
            else:
                raise RuntimeError(resp_json['message'])
            time.sleep(1)

        # 登录成功，获取姓名
        resp = self.session.get(self.main_page_url)
        print(re.search('nick: \'(.*?)\'', resp.text).group(1), '登录成功!')
        return self.session


if __name__ == '__main__':
    x = zjuamPC('', '')
    # x = zjuamScanqr()
    x.login()
