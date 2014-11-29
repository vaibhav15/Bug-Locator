
from django.conf.urls import patterns, url
from buglocator import views
from django.conf import settings

urlpatterns = patterns('buglocator.views',
    url(r'^dashboard/$','list',name='list'),
    url(r'^user/$','login',name='login'),
    url(r'^registration/$','registration',name='registration'),
    url(r'^$','homepage',name='homepage'),
    url(r'^reportbug/$','reportbug',name='reportbug'),    
)
