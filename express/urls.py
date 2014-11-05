from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'token/$', views.token, name='token'),
	url(r'detail/(.*)$', views.detail, name='detail'),
	)