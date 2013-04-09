from django.conf.urls import patterns, url

from .views import ChatRoom, CreateMessage
from chat.views import CreateRoom
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
    url(r'^$', login_required(CreateRoom.as_view()), name='lobby'),
    url(r'^(?P<room>.+)/msg/$', login_required(CreateMessage.as_view()), name='create_message'),
    url(r'^(?P<room>.+)/$', login_required(ChatRoom.as_view()), name='chatroom'),
)
