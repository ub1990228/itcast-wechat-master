WEIXIN_TOKEN = 'itcast_wechat'
WEIXIN_APPID = 'wx63afd8910ac82737'
WEIXIN_APPSECRET = '06abca4d83a582c46a37957c4c499ba2'

CREATE_MENU_URL = 'http://www.itcastcpp.cn/user_info/'
HOME_URL = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=' + WEIXIN_APPID + '&redirect_uri=' + CREATE_MENU_URL + '&response_type=code&scope=snsapi_base&state=snsapi_base#wechat_redirect'

WEIXIN_ACCESS_TOKEN_URL = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=' + WEIXIN_APPID + '&secret=' + WEIXIN_APPSECRET
WEIXIN_ACCESS_TOKEN = ''
WEIXIN_ACCESS_TOKEN_LASTTIME = 0
WEIXIN_ACCESS_TOKEN_EXPIRES_IN = 0
