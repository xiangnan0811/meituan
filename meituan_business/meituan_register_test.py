import execjs
import requests


class MeituanLogin:

    def __init__(self, username, password, mobile=None):
        self.session = requests.session()
        self.mobile = mobile
        self.username = username
        self.password = password
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
        }

    @staticmethod
    def get_rohr_token():
        rohr_url = "https://epassport.meituan.com/api/account/login?loginContinue=https://kd.meituan.com/setbtoken?source=9&redirect=https%3A%2F%2Fkd.meituan.com%2Flogin%3Fsource%3D9&&only_auth=undefined"
        token_js = open('rohr_token.js', 'r', encoding='utf8').read()
        ctx = execjs.compile(token_js)
        token = ctx.call("get_token", rohr_url)
        return token

    def update_headers(self):
        self.headers.update({
            "x-requested-with": "XMLHttpRequest",
            "Host": "epassport.meituan.com",
            "Origin": "https://epassport.meituan.com",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
        })

    def prelogin(self):
        login_page_url = "http://e.waimai.meituan.com/new_fe/login"
        self.session.get(url=login_page_url, headers=self.headers)
        self.update_headers()

    def sms(self, login_type="mobile", verify_event=2):
        sms_url = "https://epassport.meituan.com/api/biz/auth/sms"
        params = {"service": "waimai", "bg_source": "3", "part_type": "0"}
        payload = {
            "login": self.username,
            "mobile": self.mobile,
            "sms_code": "",
            "intercode": "86",
            "isFetching": False,
            "success": "",
            "error": "",
            "loginType": login_type,
            "verify_event": 2,
        }
        if verify_event == 8:
            payload = {"verify_event": 8, "login": self.username, "part_key": "", "smsCode": "", "smsVerify": 1}

        response = self.session.post(url=sms_url, params=params, data=payload, headers=self.headers)
        return response.json()

    def sms_login(self, sms_code, login_type="mobile"):
        sms_login_url = "https://epassport.meituan.com/api/account/login"
        continue_url = "https://kd.meituan.com/setbtoken?source=38&redirect=https%3A%2F%2Fkd.meituan.com%2Flogin%3Fsource%3D38"
        payload = {
            "mobile": self.mobile,
            "sms_code": sms_code,
            "intercode": "86",
            "isFetching": False,
            "success": "",
            "error": "",
            "loginType": login_type,
            "continue": continue_url,
            "rohrToken": self.get_rohr_token(),
        }
        params = {
            "service": "kaidian",
            "bg_source": "3",
            "part_type": "0",
            "loginContinue": continue_url,
            "loginType": login_type,
        }
        self.update_headers()
        res = self.session.post(url=sms_login_url, headers=self.headers, data=payload, params=params)
        return res.json()

    def account_login(self, login_type="account"):
        account_login_url = "https://epassport.meituan.com/api/account/login"
        payload = {
            "login": self.username,
            "part_key": "",
            "password": self.password,
            "error": "账号或密码错误",
            "success": "",
            "isFetching": False,
            "loginType": login_type,
            "verifyRequestCode": "",
            "verifyResponseCode": "",
            "captchaCode": "",
            "verifyType": None,
            "captchaToken": "",
            "rohrToken": self.get_rohr_token(),
        }
        params = {
            "service": "kaidian",
            "bg_source": "3",
            "part_type": "0",
            "loginContinue": "https:%2F%2Fkd.meituan.com%2Fsetbtoken%3Fsource%3D38%26redirect%3Dhttps%253A%252F%252Fkd.meituan.com%252Flogin%253Fsource%253D38",
            "loginType": login_type,
        }
        self.update_headers()
        self.headers.update({"Referer": "https://epassport.meituan.com/account/unitivelogin?bg_source=3&service=waimai&platform=2&continue=http%3A%2F%2Fe.waimai.meituan.com%2Fnew_fe%2Flogin%23%2Flogin%2Fcontinue&left_bottom_link=%2Faccount%2Funitivesignup%3Fbg_source%3D3%26service%3Dwaimai%26platform%3D2%26extChannel%3Dwaimaie%26ext_sign_up_channel%3Dwaimaie%26continue%3Dhttp%3A%2F%2Fe.waimai.meituan.com%2Fv2%2Fepassport%2FsignUp&right_bottom_link=%2Faccount%2Funitiverecover%3Fbg_source%3D3%26service%3Dwaimai%26platform%3D2%26continue%3Dhttp%3A%2F%2Fe.waimai.meituan.com%252Fnew_fe%252Flogin%2523%252Flogin%252Frecover&"})
        response = self.session.post(url=account_login_url, params=params, data=payload, headers=self.headers)
        res_json = response.json()
        if res_json["status"]["code"] == 5002:
            self.sms(verify_event=8)
            sms_code = input("输入短信验证码：")
            res = self.sms_login(sms_code=sms_code, login_type="account")
            res_json = res.json()
        elif res_json["status"]["code"] == 2017:
            print("需要滑块验证")
            res_json = {"code": 2017, "message": "需要滑块验证"}
        elif res_json["status"]["code"] == 2002:
            print("需要短信验证")
            res_json = {"code": 2002, "message": "需要短信验证"}
        elif res_json["status"]["code"] == 1001:
            print("账号或密码错误")
            res_json = {"code": 1001, "message": "账号或密码错误"}
        return res_json

    def login(self, login_type):
        if login_type == "account":
            res = self.account_login(login_type)
        elif login_type == "mobile":
            self.sms(login_type)
            sms_code = input("输入短信验证码：")
            res = self.sms_login(sms_code)
        else:
            res = None
        return res


if __name__ == '__main__':
    login_spider = MeituanLogin(username="xiangnan7171", password="13720929258Ber", mobile="19180974915")
    res = login_spider.login(login_type="account")
    print(res)
