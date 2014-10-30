#coding:utf-8
import os
os.environ['DJANGO_SETTINGS_MODULE'] = "WeChat.settings"

from express.models import *
import requests
from datetime import datetime
import simplejson as json

def test():
	wechat_objs = WeChatBase.objects.all()
	print wechat_objs

def getAccessToken():
	wechat_objs = WeChatBase.objects.all()
	if wechat_objs:
		if (datetime.now()-wechat_objs[0].wc_time).seconds > wechat_objs[0].wc_expirs_in:
			try:
				response = requests.get('https://api.weixin.qq.com/cgi-bin/token', params={'grant_type':'client_credential','appid':wechat_objs[0].wc_appid,'secret':wechat_objs[0].wc_secret})
				response.raise_for_status()
			except requests.RequestException as e:
				print (e)
			else:
				result = response.json()
				print result,type(result)
				wechat_objs[0].wc_time = datetime.now()
				wechat_objs[0].wc_access_token = result['access_token']
				wechat_objs[0].wc_expirs_in = result['expires_in']
				wechat_objs[0].save()
	wechat_objs = WeChatBase.objects.all()
	return	wechat_objs[0].wc_access_token

def setMenu():
	data = '''{"button":[
				{"type": "scancode_push","name":"扫码查询","key":"scan"},
				{"type": "click","name":"单号查询","key":"code"},
				{"type": "view","name":"关于我们","url":"http://www.congyuandong.cn"}
					]
			}'''
	response = requests.post('https://api.weixin.qq.com/cgi-bin/menu/create?access_token='+getAccessToken(),data=data)
	print response.json()

if __name__ == '__main__':
	setMenu()

