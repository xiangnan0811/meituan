from flask import Flask
from meituan_register_test import MeituanLogin
app = Flask(__name__)


@app.route('/')
def hello_world():
    login_spider = MeituanLogin(username="xiangnan7171", password="13720929258Ber", mobile="19180974915")
    res = login_spider.login()
    print(res)
    # res = login_spider.sms()
    # print(res)
    return res


if __name__ == '__main__':
    app.run()
