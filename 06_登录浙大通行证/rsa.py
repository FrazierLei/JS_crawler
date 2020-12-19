import execjs
import requests

def get_js_function(js_path, func_name, *args):
    '''
    获取指定目录下的js代码, 并且指定js代码中函数的名字以及函数的参数。
    :param js_path: js代码的位置
    :param func_name: js代码中函数的名字
    :args: js代码中函数的参数
    :return: 返回调用js函数的结果
    '''

    with open(js_path, encoding='utf-8') as fp:
        js = fp.read()
        ctx = execjs.compile(js)
        return ctx.call(func_name, *args)

if __name__ == '__main__':
    params = requests.get('https://zjuam.zju.edu.cn/cas/v2/getPubKey').json()
    # exponent, modulus = params['exponent'], params['modulus']
    exponent = "10001"
    modulus = "a855b2dd6b714bb629a031eaa1b722b1d752256d44c82957d1f91c8e7aceb3a67c73be8bd4dfc0df0a8c78eea2a9f1760385e5a4eda6fd2428dd1d07d58992f3"

    original_pwd = '123456'
    encryped_pwd = get_js_function('zjuam.js', 'checkForm', exponent, modulus, original_pwd)
    print('原密码：', original_pwd)
    print('加密密码：', encryped_pwd)
