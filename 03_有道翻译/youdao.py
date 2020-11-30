import time
import requests
from hashlib import md5

def youdao_translator(sentence):
    
    # 获取参数
    lts = str(int(time.time() * 1000))
    salt = str(int(time.time() * 10000))
    ua = '5.0 (Macintosh; Intel Mac OS X 11_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36'
    bv = md5(ua.encode()).hexdigest()
    sign = md5(('fanyideskweb' + sentence + salt + ']BjuETDhU)zqSxf-=B#7m').encode()).hexdigest()
    
    # 创建一个会话来获取cookie
    s = requests.session()
    s.get('http://fanyi.youdao.com')
    
    # headers中必要的三个参数，其他的都不必要
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Referer': 'http://fanyi.youdao.com/',
    }

    data = {
      'i': sentence,
      'from': 'AUTO',
      'to': 'AUTO',
      'smartresult': 'dict',
      'client': 'fanyideskweb',
      'salt': salt,
      'sign': sign,
      'lts': lts,
      'bv': bv,
      'doctype': 'json',
      'version': '2.1',
      'keyfrom': 'fanyi.web',
      'action': 'FY_BY_REALTlME'
    }

    r = s.post('http://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule', headers=headers, data=data)
    return r.json()['translateResult'][0][0]['tgt']
  

if __name__ == '__main__':
  	print(youdao_translator('不想学习'))