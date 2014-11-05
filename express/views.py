#coding:utf-8
from django.shortcuts import render
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from models import *
import requests
from datetime import datetime
import time
from xml.etree import ElementTree

import hashlib

REPLAY_TEXT = """<xml>
    <ToUserName><![CDATA[%s]]></ToUserName>
    <FromUserName><![CDATA[%s]]></FromUserName>
    <CreateTime>%s</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[%s]]></Content>
    </xml>"""

MESSAGE_TEXT_PICTURE = """<xml>
    <ToUserName><![CDATA[%s]]></ToUserName>
    <FromUserName><![CDATA[%s]]></FromUserName>
    <CreateTime>%s</CreateTime>
    <MsgType><![CDATA[news]]></MsgType>
    <ArticleCount>1</ArticleCount>
    <Articles>
    <item>
    <Title><![CDATA[%s]]></Title>
    <Description><![CDATA[%s]]></Description>
    <Url><![CDATA[%s]]></Url>
    </item>
    </Articles>
    </xml>"""

def index(request):
	context = RequestContext(request)
	context_dict = {}
	return render_to_response('express/index.html',context_dict,context)

#获取access_token
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

@csrf_exempt
def token(request):
	if request.method=='GET':
		response=HttpResponse(checkSignature(request))
		return response
	else:
		return doPost(request)

def doPost(request):
	xml = ElementTree.fromstring(request.body)
	message_type = xml.find("MsgType").text
	print message_type
	if message_type == 'event':
		return event_receiver(request)
	elif message_type == 'text':
		return message_receiver(request)
	else:
		print("无效请求，MsgType：" + message_type)
		return HttpResponse("invalid request")

def event_receiver(request):
	xml = ElementTree.fromstring(request.body)
	server_id = xml.find("ToUserName").text
	user_open_id = xml.find("FromUserName").text
	event = xml.find("Event").text
	print("接收到事件："+event)
	if event == "CLICK":
		key = xml.find("EventKey").text
		#return wss_tools.message_handler(request,key)
		return click_handler(request,key)
	elif event == "scancode_waitmsg":
		key = xml.find("EventKey").text
		return scan_handler(request,key)

def click_handler(request,key):
	xml = ElementTree.fromstring(request.body)
	toUserName = xml.find("ToUserName").text
	fromUserName = xml.find("FromUserName").text
	return text_response(from_user_name=toUserName, to_user_name=fromUserName, text="请点击键盘图标;\n直接输入单号即可!")

#扫码事件
def scan_handler(request,key):
	xml = ElementTree.fromstring(request.body)
	toUserName = xml.find("ToUserName").text
	fromUserName = xml.find("FromUserName").text
	scanResult = xml.find("ScanCodeInfo").find("ScanResult").text
	#return text_response(from_user_name=toUserName, to_user_name=fromUserName, text=scanResult)
	return code_handler(request,scanResult)

#输入快递单号
def message_receiver(request):
	xml = ElementTree.fromstring(request.body)
	content = xml.find("Content").text.encode('utf-8')
	#return message_handler(request, content)
	return code_handler(request,content)

def message_handler(request,content):
	xml = ElementTree.fromstring(request.body)
	toUserName = xml.find("ToUserName").text
	fromUserName = xml.find("FromUserName").text
	return text_response(from_user_name=toUserName, to_user_name=fromUserName, text=content)

# 回复文字
def text_response(to_user_name, from_user_name, text):
	post_time = str(int(time.time()))
	return HttpResponse(REPLAY_TEXT % (to_user_name, from_user_name, post_time, text))

#返回订单URL
def code_handler(request,code):
	xml = ElementTree.fromstring(request.body)
	toUserName = xml.find("ToUserName").text
	fromUserName = xml.find("FromUserName").text
	#url = requests.get('http://www.kuaidi100.com/applyurl', params={'key':'4eadc5f4e1f608eb','com':'shunfeng','nu':code})
	#url = url.content
	#title = "订单号："+code
	getTrack(code)
	url = 'http://wechat.congyuandong.cn'
	return url_response(from_user_name=toUserName, to_user_name=fromUserName,title=title,desc="点击查看最新物流信息",url=url)

#将订单数据存入数据库
def getTrack(code):
	url = 'http://222.66.109.133/track.aspx'
	params = {'billcode':code}
	response = requests.get(url, params=params)
	response = r.content.decode('gb2312').encode('utf-8')
	response = response.replace('gb2312','utf-8')

	xml = ElementTree.fromstring(response)
	details = xml.getiterator("detail")

	if len(details) > 0:
		TrackAdmin_objs = TrackAdmin.objects.filter(billcode__exact = code)
		if TrackAdmin_objs:
			for TrackAdmin_obj in TrackAdmin_objs:
				TrackAdmin_obj.delete()
		for detail in details:
			time = datetime.strptime(detail.find('time').text, "%Y/%m/%d %H:%M:%S")  
			scantype = detail.find('scantype').text
			memo = detail.find('memo').text
			TrackAdmin_new = TrackAdmin(billcode=code,scantype=scantype,memo=memo,time=time)
			TrackAdmin.save()
	else:
		print 'None'

def url_response(from_user_name, to_user_name,title,desc,url):
	post_time = str(int(time.time()))
	#picUrl = 'http://www.baidu.com/img/bdlogo.png'
	return HttpResponse(MESSAGE_TEXT_PICTURE % (to_user_name, from_user_name,post_time,title,desc,url))


def checkSignature(request):
	signature=request.GET.get('signature',None)
	timestamp=request.GET.get('timestamp',None)
	nonce=request.GET.get('nonce',None)
	echostr=request.GET.get('echostr',None)

	wechat_objs = WeChatBase.objects.all()
	if wechat_objs:
		token = wechat_objs[0].wc_token
		print token
		tmplist = [token,timestamp,nonce]
		tmplist.sort()
		tmpstr="%s%s%s"%tuple(tmplist)
		tmpstr=hashlib.sha1(tmpstr).hexdigest()
		if tmpstr==signature:
			return echostr
		else:
			return None
	return None