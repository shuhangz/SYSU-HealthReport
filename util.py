import requests
import onnxruntime
from PIL import Image,ImageEnhance
import numpy as np
from time import sleep
session=requests.Session()

def getCaptcha(filePath = 'captcha.jpg'):
        # 识别
        key_map={48: '0', 49: '1', 50: '2', 51: '3', 52: '4', 53: '5', 54: '6', 55: '7', 56: '8', 57: '9',
         97: 'a', 98: 'b', 99: 'c', 100: 'd', 101: 'e', 102: 'f', 103: 'g', 104: 'h', 105: 'i', 106: 'j', 107: 'k', 108: 'l', 109: 'm', 110: 'n', 111: 'o', 112: 'p', 113: 'q', 114: 'r', 115: 's', 116: 't', 117: 'u', 118: 'v', 119: 'w', 120: 'x', 121: 'y', 122: 'z'}
        img_file=Image.open(f"{os.environ['GITHUB_ACTION_PATH']}/%s" %filePath)
        img_file=img_file.convert("RGBA")
        inputs=np.array(img_file)
        inputs=inputs.ravel()
        inputs=self.convert2array(inputs,90,32)
        inputs=np.array(inputs)
        session1=onnxruntime.InferenceSession(f"{os.environ['GITHUB_ACTION_PATH']}/cnn.onnx")
        input_name = session1.get_inputs()
        pred=session1.run([],{input_name[0].name:inputs.astype(np.float32).reshape(1,3,90,32)})
        pred=pred[0].flatten()
        strs=""
        for t in range(4):
            a=pred[t*36:(t+1)*36]
            ans=np.argmax(a)
            if ans>=0 and ans <26:
                strs +=key_map[ans+97]
            else:
                strs +=key_map[ans+22]
        strs=''.join(re.findall(r'[a-zA-Z0-9]',strs))
        return strs[0:4]
    
    
def get_img1(driver):
    headers = {'Connection': 'Keep-Alive',
        'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)'}
    cookies=driver.get_cookies()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    captcha_url = 'https://cas.sysu.edu.cn/cas/captcha.jsp'
    response = session.get(captcha_url, headers=headers)
    sleep(5)
    with open(f"{os.environ['GITHUB_ACTION_PATH']}/captcha.jpg", "wb") as f:
        f.write(response.content)
    sleep(3)
    captcha = getCaptcha()
    sleep(1.5)
    #判断文件是否存在
    if(os.path.exists(f"{os.environ['GITHUB_ACTION_PATH']}/captcha.jpg")):
        os.remove(f"{os.environ['GITHUB_ACTION_PATH']}/captcha.jpg")
        print("移除目录下文件")
    else:
        print("要删除的文件不存在！")
    return captcha
    
def get_img(driver, token):
    ''' 调用 http://fast.95man.com 在线识别验证码
    '''

    headers = {'Connection': 'Keep-Alive',
        'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)'}
    cookies = driver.get_cookies()
    s = requests.Session()
    for cookie in cookies:
        s.cookies.set(cookie['name'], cookie['value'])

    url = "https://cas.sysu.edu.cn/cas/captcha.jsp"
    res =  s.get(url)
    
    if token.startswith('RECURL'):
        files = {'img': ('captcha.jpg', res.content, 'image/jpeg')}
        r =  requests.post(token[6:], files = files)
        if len(r.text) == 4:
            capt = r.text
            print(f'验证码识别成功：{capt}')
            return capt
        else:
            print(f'识别失败：{r.text}，重试')
            raise Exception('验证码识别失败')
    else:
        files = {'imgfile': ('captcha.jpg', res.content)}
        r = requests.post(f'http://api.95man.com:8888/api/Http/Recog?Taken={token}&imgtype=1&len=4', 
            files=files, headers=headers)
        arrstr = r.text.split('|')
        # 返回格式：识别ID|识别结果|用户余额
        if(int(arrstr[0]) > 0):
            print(f'验证码识别成功：{arrstr[1]}')
            capt = arrstr[1]
            return capt
        else:
            print(f'识别失败：{arrstr[1]}，重试')
            raise Exception('验证码识别失败')


def tgbot_send(token, chatid, message):
    data = {'chat_id': chatid, 'text': f'健康申报结果：{message}'}
    try:
        r = requests.post(f'https://api.telegram.org/bot{token}/sendMessage', data = data)
        if r.status_code == 200:
            print('发送通知成功')
        else:
            print('发送通知失败')
    except:
        print('发送通知失败')


def wx_send(wxsend_key, message):
    data = {
        "title": f'健康申报结果：{message}',
        "desp": "如遇身体不适、或居住地址发生变化，请及时更新健康申报信息。"
    }
    try:
        r = requests.post(f'https://sctapi.ftqq.com/{wxsend_key}.send', data = data)
        if r.status_code == 200:
            print('发送通知成功')
        else:
            print('发送通知失败')
    except:
        print('发送通知失败')
