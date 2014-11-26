
from django.conf.urls import patterns, url
from buglocator import views

urlpatterns = patterns('buglocator.views',
    url(r'^list/$','list',name='list'),
    url(r'^login/$','login',name='login'),
    url(r'^registration/$','registration',name='registration'),
)
