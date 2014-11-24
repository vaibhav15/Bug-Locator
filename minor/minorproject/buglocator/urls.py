
from django.conf.urls import patterns, url
from buglocator import views

urlpatterns = patterns('buglocator.views',
    url(r'^list/$','list',name='list'),
)
