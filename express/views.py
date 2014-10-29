#coding:utf-8
from django.shortcuts import render
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

import hashlib


WECHAT_TOKEN = 'congyuandong2014'


def index(request):
	context = RequestContext(request)
	context_dict = {}
	return render_to_response('express/index.html',context_dict,context)

@csrf_exempt
def token(request):
    if request.method=='GET':
        response=HttpResponse(checkSignature(request))
        return response
    else:
        return HttpResponse('Hello World')

def checkSignature(request):
    signature=request.GET.get('signature',None)
    timestamp=request.GET.get('timestamp',None)
    nonce=request.GET.get('nonce',None)
    echostr=request.GET.get('echostr',None)
    #这里的token我放在setting，可以根据自己需求修改
    token=WECHAT_TOKEN

    tmplist=[token,timestamp,nonce]
    tmplist.sort()
    tmpstr="%s%s%s"%tuple(tmplist)
    tmpstr=hashlib.sha1(tmpstr).hexdigest()
    if tmpstr==signature:
        return echostr
    else:
        return None