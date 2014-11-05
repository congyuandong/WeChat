from django.contrib import admin
from models import *

# Register your models here.

class WeChatBaseAdmin(admin.ModelAdmin):
	fields = ['wc_token','wc_appid','wc_secret','wc_expirs_in','wc_time','wc_access_token']
	list_display = ['wc_token','wc_appid','wc_secret','wc_expirs_in','wc_time','wc_access_token']

class TrackAdmin(admin.ModelAdmin):
	list_display = ['billcode','time','scantype','memo']


admin.site.register(WeChatBase,WeChatBaseAdmin)
admin.site.register(Track,TrackAdmin)