# -*- coding: utf-8 -*-
import datetime
import time
import json
import random
import base64
import hashlib
import hmac
import urllib
import zlib

import requests
import requests.exceptions

#=====================================================================================
HEADER = {'Accept-Encoding': 'identity',
          'Connection': 'Keep-Alive',
          'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 5.1.1; mi max Build/LMY48Z)'}

class Session:
    def __init__(self):
        self.session = requests.session()

    def new_session(self):
        self.session = requests.session()
        self.session.keep_alive = False

    def get(self, url, **kwargs):
        for i in range(5):
            try:
                r = self.session.get(url=url, **kwargs)
                r.close()
                return r
            except requests.exceptions.ConnectTimeout:
                if i == 4:
                    raise

    def post(self, url, data=None, json=None, **kwargs):
        for i in range(5):
            try:
                r = self.session.post(url=url, data=data, json=json, **kwargs)
                r.close()
                return r
            except requests.exceptions.ConnectTimeout:
                if i == 4:
                    raise

session = Session()

#=================================================================================

class GameLogin:
    """
    1st login: channal cookie version server_list
    2nd login: return nothing; init data
    """
    def __init__(self):
        self.pastport_headers = {
            "Accept-Encoding": "gzip",
            'User-Agent': 'okhttp/3.4.1',
            "Content-Type": "application/json; charset=UTF-8"
        }
        self.init_data_version = "0"
        self.hm_login_server = ""
        self.portHead = ""
        self.key = "kHPmWZ4zQBYP24ubmJ5wA4oz0d8EgIFe"
        self.login_server = ""
        self.res = ""

        self.version = "4.8.0"
        self.channel = '100015'
        self.cookies = None
        self.server_list = []
        self.defaultServer = 0
        self.uid = None

    def first_login_usual(self, server, username, pwd):
        # iOS
        url_version = 'http://version.jr.moefantasy.com/' \
                      'index/checkVer/4.8.0/100015/2&version=4.8.0&channel=100015&market=2'
        self.res = 'http://loginios.jr.moefantasy.com/index/getInitConfigs/'
        self.channel = "100015"
        self.portHead = "881d3SlFucX5R5hE"
        self.key = "kHPmWZ4zQBYP24ubmJ5wA4oz0d8EgIFe"
        # -------------------------------------------------------------------------------------------
        # 拉取版本信息
        response_version = session.get(url=url_version, headers=HEADER, timeout=10)
        response_version = response_version.text
        response_version = json.loads(response_version)

        # 获取版本号, 登录地址
        self.version = response_version["version"]["newVersionId"]
        self.login_server = response_version["loginServer"]
        self.hm_login_server = response_version["hmLoginServer"]

        # -------------------------------------------------------------------------------------------
        # 进行登录游戏
        server_data = self.login_usual(server=server, username=username, pwd=pwd)

        self.defaultServer = int(server_data["defaultServer"])
        self.server_list = server_data["serverList"]
        self.uid = server_data["userId"]

        return_data = {
            "version": self.version,
            "channel": self.channel,
            "cookie": self.cookies,
            "server_list": self.server_list,
            "default_server": self.defaultServer,
            "uid": self.uid
        }
        return True

    def second_login(self, host, uid):
        # 生成随机设备码
        now_time = str(int(round(time.time() * 1000)))
        random.seed(hashlib.md5(self.uid.encode('utf-8')).hexdigest())
        data_dict = {'client_version': self.version,
                     'phone_type': 'huawei tag-al00',
                     'phone_version': '5.1.1',
                     'ratio': '1280*720',
                     'service': 'CHINA MOBILE',
                     'udid': str(random.randint(100000000000000, 999999999999999)),
                     'source': 'android',
                     'affiliate': 'WIFI',
                     't': now_time,
                     'e': self.get_url_end(now_time),
                     'gz': '1',
                     'market': '2',
                     'channel': self.channel,
                     'version': self.version
                     }
        random.seed()
        # 获取欺骗数据
        login_url_tmp = host + 'index/login/' + uid + '?&' + urllib.parse.urlencode(data_dict)
        session.get(url=login_url_tmp, headers=HEADER, cookies=self.cookies, timeout=10)

        url_cheat = host + 'pevent/getPveData/' + self.get_url_end()
        session.get(url=url_cheat, headers=HEADER, cookies=self.cookies, timeout=10)

        url_cheat = host + 'shop/canBuy/1/' + self.get_url_end()
        session.get(url=url_cheat, headers=HEADER, cookies=self.cookies, timeout=10)
        
        url_cheat = host + 'live/getUserInfo' + self.get_url_end()
        session.get(url=url_cheat, headers=HEADER, cookies=self.cookies, timeout=10)
        
        url_cheat = host + 'live/getMusicList/' + self.get_url_end()
        session.get(url=url_cheat, headers=HEADER, cookies=self.cookies, timeout=10)
        
        url_cheat = host + 'bsea/getData/' + self.get_url_end()
        session.get(url=url_cheat, headers=HEADER, cookies=self.cookies, timeout=10)
        
        url_cheat = host + 'active/getUserData' + self.get_url_end()
        session.get(url=url_cheat, headers=HEADER, cookies=self.cookies, timeout=10)

        url_cheat = host + 'pve/getUserData/' + self.get_url_end()
        session.get(url=url_cheat, headers=HEADER, cookies=self.cookies, timeout=10)

        return True

    # 普通登录实现方法
    def login_usual(self, username, pwd, server):

        url_login = self.hm_login_server + "1.0/get/login/@self"
        data = {
            "platform": "0",
            "appid": "0",
            "app_server_type": "0",
            "password": pwd,
            "username": username
        }

        self.refresh_headers(url_login)

        login_response = session.post(url=url_login, data=json.dumps(data).replace(" ", ""),
                                      headers=self.pastport_headers, timeout=10).text
        login_response = json.loads(login_response)

        if "error" in login_response and int(login_response["error"]) != 0:
            return False

        tokens = ""
        if "access_token" in login_response:
            tokens = login_response["access_token"]
        if "token" in login_response:
            tokens = login_response["token"]

        url_init = self.hm_login_server + "1.0/get/initConfig/@self"
        self.refresh_headers(url_init)
        session.post(url=url_init, data="{}", headers=self.pastport_headers, timeout=10)
        time.sleep(1)

        # Validate token
        while True:
            url_info = self.hm_login_server + "1.0/get/userInfo/@self"

            login_data = json.dumps({"access_token": tokens})

            self.refresh_headers(url_info)
            user_info = session.post(url=url_info, data=login_data, headers=self.pastport_headers, timeout=10).text
            user_info = json.loads(user_info)
            if "error" in user_info and user_info["error"] != 0:
                tokens = ""
                continue
            else:
                break

        login_url = self.login_server + "index/hmLogin/" + tokens + self.get_url_end()
        login_response = session.get(url=login_url, headers=HEADER, timeout=10)
        login_text = json.loads(zlib.decompress(login_response.content))

        self.cookies = login_response.cookies.get_dict()
        self.uid = str(login_text['userId'])
        return login_text

    def get_url_end(self, now_time=str(int(round(time.time() * 1000)))):
        url_time = now_time
        md5_raw = url_time + 'ade2688f1904e9fb8d2efdb61b5e398a'
        md5 = hashlib.md5(md5_raw.encode('utf-8')).hexdigest()
        url_end = '&t={time}&e={key}&gz=1&market=2&channel={channel}&version={version}'
        url_end_dict = {'time': url_time, 'key': md5, 'channel': self.channel, 'version': self.version}
        url_end = url_end.format(**url_end_dict)
        return url_end

    def encryption(self, url, method):
        times = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

        data = str(method) + "\n" + times + "\n" + "/" + url.split("/", 3)[-1]
        mac = hmac.new(self.key.encode(), data.encode(), hashlib.sha1)
        data = mac.digest()
        return base64.b64encode(data).decode("utf-8"), times

    def refresh_headers(self, url):
        data, times = self.encryption(url=url, method="POST")
        self.pastport_headers["Authorization"] = "HMS {}:".format(self.portHead) + data
        self.pastport_headers["Date"] = times

    # ================================================================
    # Game Functions
    # ================================================================

    def get_login_reward(self):
        url = self.server_list[0]["host"] + 'active/getLoginAward/c3ecc6250c89e88d83832e3395efb973/' + self.get_url_end()
        data=self.decompress_data(url)
        data = json.loads(data)
        return data

    def get_friend_list(self):
        url = self.server_list[0]["host"] + 'friend/getlist' + self.get_url_end()
        raw_data = self.decompress_data(url)
        data = json.loads(raw_data)
        return data["list"]
    
    def friend_feat(self, uid, cook_item):
        url = self.server_list[0]["host"] + 'live/feat/' + uid + '/' + cook_item + self.get_url_end()
        raw_data = self.decompress_data(url)
        data = json.loads(raw_data)
        return data

    def visit_friend_kitchen(self, uid):
        url = self.server_list[0]["host"] + 'live/friendKitchen/' + uid + self.get_url_end()
        raw_data = self.decompress_data(url)
        data = json.loads(raw_data)
        return data

    def decompress_data(self,url,*vdata):
        if  len(vdata) is 0:
            content = session.get(url=url, headers=HEADER, cookies=self.cookies, timeout=10).content
        else:
            h = HEADER
            h["Content-Type"]="application/x-www-form-urlencoded"
            content = session.post(url=url,data=str(vdata[0]), headers=h, cookies=self.cookies, timeout=10).content

        try:
            data = zlib.decompress(content)
        except Exception as e:
            data = content
        return data


if __name__ == "__main__":
    MY_ACCOUNTS = {}
    with open('acc2.json', 'r') as f:
        MY_ACCOUNTS = json.load(f)

    # Quotidian limit is 3 orders per user
    # Quotidian increase limit for target user is 100 points

    account_num = 0
    while account_num < len(MY_ACCOUNTS):
        t = GameLogin()

        res1 = t.first_login_usual(1, MY_ACCOUNTS[account_num]["id"], MY_ACCOUNTS[account_num]["pswd"])
        res2 = t.second_login(t.server_list[0]["host"], MY_ACCOUNTS[account_num]["uid"])
        if res1 is True and res2 is True:
            print("[INFO] Successfully logged in with uid: {}".format(MY_ACCOUNTS[account_num]["uid"]))
        else:
            print("[WARNING] Skip {}".format(MY_ACCOUNTS[account_num]["id"]))
            account_num = account_num + 1
            continue

        print("[INFO] Getting login reward...")
        print(t.get_login_reward())

        all_friend_list = t.get_friend_list()
        print(all_friend_list)
        for friend in all_friend_list:
            k = t.visit_friend_kitchen(friend['uid'])
            print("[INFO] Kitchen popularity of target account: {}/10000".format(k['popularity']))
            if k['eatTimes'] >= 3:
                print("[ERROR] Reaches quotidian dining limit.")
                continue
            m = k['shipVO']['cookbook']             # get menu, a vector of 3 strings
            for x in range(3):                      # 3 times per day
                # TODO: in future, eat non-max menu to improve proficiency
                t.friend_feat(friend['uid'], m[0])

        account_num = account_num + 1
        print("================================================================")