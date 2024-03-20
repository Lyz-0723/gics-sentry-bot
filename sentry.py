import requests
from dotenv import get_key
from time import sleep
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5
from base64 import b64decode, b64encode
import os

# 關掉 pygame 歡迎訊息
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame import mixer

# 在 .env 中填入競賽用的帳號密碼
# alert_if_script_down: 程式異常（例如網路斷掉）時，要不要播音樂警告
# competition_name: 競賽在 PaGamO 上的代號，例如 2024gics_college
alert_if_script_down = True
competition_name = '2024gics_college'
account = get_key('.env', 'ACCOUNT')
password = get_key('.env', 'PASSWORD')

last_seen_score = -1
public_key = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA7PIWyhn3rvv4B9UWMTriKb0J1HsAkoC25YYDoGmf019IxAgDdQZtu6fVeQIbfexQNN5qX+2hyiKUMnL+Bcllvxk1aGQVggKtNr9XAGdQjVsisLROi/VHuQoYGUxcF0TxxEgEW98uXn63Ub+uAsxadV0Tr2y5d1pFVUIVBQeXiDIS1pY1kzE0oGMN4l4/3xow973kmN6Lo3sIB8vIioeXbYUY2okZm54BpLSqtxOWp/WQlimOkZ0nJwvNr5g94PCRrBvDMCt7QlwA6VUzqPLZ0RVrWL2+JgQV/ujWFZKvOcXtoftYwjogiFPDDhQ5GQxjW/ZdswNMs0k7RPx3jmyJJwIDAQAB'
rsa_key = RSA.importKey(b64decode(public_key))
cipher_text = Cipher_PKCS1_v1_5.new(rsa_key).encrypt(password.encode())
e_pw = b64encode(cipher_text)
login_url = 'https://esports.pagamo.org/api/sign_in'
# TODO: to 參數可能會需要更新，待競賽開始後確認
login_data = {'to': f'%/contests%/{competition_name}', 'account': account, 'encrypted': True, 'password': e_pw}

s = requests.Session()
resp = s.post(login_url, data=login_data)

ignore = 0
ranking_url = 'https://esports.pagamo.org/esports/instant_rankings'
ranking_params = {'ranking_type':'contest_by_team'}

resp = s.get(ranking_url, params=ranking_params)
while resp.status_code == 200:
    try:
        current_score =  resp.json()["data"]["self_rankings"]["score"]
        if last_seen_score > current_score:
            if not ignore:
                print('警告: 偵測到入侵!')
                print(f'原本分數: {last_seen_score}, 現在分數: {current_score}')
                
                mixer.init()
                mixer.music.load('./alarm.mp3')
                mixer.music.play()
                while mixer.music.get_busy():
                    sleep(1) # 等待音樂結束撥放

                last_seen_score = current_score
                ignore = 3 # 三次內分數繼續減少不警告
            else:
                ignore -= 1
        else:
            print(f'哨兵監視中, 目前分數: {current_score}')
        
        sleep(180) # 每三分鐘檢查一次
        resp = s.get(ranking_url, params=ranking_params)
    except Exception as e:
        print(' {0}'.format(e))
        if alert_if_script_down:
            mixer.init()
            mixer.music.load('./alarm.mp3')
            mixer.music.play()
            while mixer.music.get_busy():
                sleep(1)
            break
        break
