#coding:utf-8
from django.db import models

# Create your models here.
class WeChatBase(models.Model):
	wc_token = models.CharField(max_length=20,verbose_name='token')
	wc_appid = models.CharField(max_length=50,verbose_name='appid')
	wc_secret = models.CharField(max_length=50,verbose_name='secret')
	wc_expirs_in = models.IntegerField(default=0,verbose_name='有效期')
	wc_time = models.DateTimeField(verbose_name="获取时间")
	wc_access_token = models.CharField(max_length=600,verbose_name='凭证信息')

	def __unicode__(self):
		return self.wc_token

	class Meta:
		verbose_name = '凭证'
		verbose_name_plural = '凭证管理'

class Track(models.Model):
	billcode = models.CharField(max_length=50,verbose_name='订单编号')
	time = models.DateTimeField(verbose_name='时间')
	scantype = models.CharField(max_length=20,verbose_name='类型')
	memo = models.CharField(max_length=200,verbose_name='详细信息')

	def __unicode__(self):
		return self.billcode

	class Meta:
		verbose_name = '物流信息'
		verbose_name_plural = '物流信息'