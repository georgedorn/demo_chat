from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django import forms
from .models import Message, Room
from django.shortcuts import get_object_or_404
from django.http.response import HttpResponse, HttpResponseRedirect
from django.core import serializers
from django.core.serializers import serialize

class ChatForm(forms.ModelForm):
    content = forms.CharField(max_length=256, label='',
                              widget=forms.TextInput(attrs={'size':100}))
    
    class Meta:
        model = Message
        exclude = ('user', 'room') #both provided by request and url, respectively

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        exclude = ('creator')

class CreateRoom(CreateView):
    model = Room
    form_class = RoomForm

    def form_valid(self, form):
        """
        A message is POSTed to this view, but the user comes from 
        the Auth middleware and the room comes from the url.
        """
        form.instance.creator = self.request.user
        return super(CreateRoom, self).form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = CreateView.get_context_data(self, **kwargs)
        context['object_list'] = Room.objects.order_by('-created')
        return context
    
class ChatRoom(ListView):
    """
    Interface to the chat room.  Handles the initial room setup,
    posts of new messages, and retrieval of new messages.
    """
    model = Message
    form_class = ChatForm
    
    def get_queryset(self):
        """
        Override the default queryset to support two operations:
        - get the last X messages from this room
        - get the last messages from the room newer than Y
        """
        room = get_object_or_404(Room, name=self.kwargs.get('room'))
        qs = Message.get_for_room(room)

        limit = int(self.request.GET.get('limit', 100)) #hard-coded default. should be in settings.
        since = int(self.request.GET.get('since', 0))
        if since:
            qs = qs.filter(pk__gt=since) #relying on primary keys being in order.
        qs = qs[0:limit] #if somebody has lagged more than 100 messages, there's a problem we can't fix
        return qs
    
    def get_context_data(self, **kwargs):
        context = ListView.get_context_data(self, **kwargs)
        context['object_list'] = context['object_list'][::-1] #reverse these at the last minute
        context['room'] = get_object_or_404(Room, name=self.kwargs.get('room'))
        context['form'] = ChatForm()
        return context

    def get_template_names(self):
        template_names = ListView.get_template_names(self)
        if self.request.is_ajax():
            template_names = [f.replace('_list', '_list_ajax') for f in template_names]
        return template_names
    
class CreateMessage(CreateView):
    form_class = ChatForm
    model = Message

    def form_valid(self, form):
        """
        A message is POSTed to this view, but the user comes from 
        the Auth middleware and the room comes from the url.
        """
        form.instance.user = self.request.user
        form.instance.room = Room.objects.get(name=self.kwargs['room'])
        return super(CreateMessage, self).form_valid(form)

    def get_success_url(self):
        """
        Return to the room's url.
        """
        room = Room.objects.get(name=self.kwargs['room'])
        return room.get_absolute_url()

    def get(self, *args, **kwargs):
        """
        Should never get here, but if somebody loads this url, redirect to chat room.
        """
        return HttpResponseRedirect(self.get_success_url())


    def post(self, request, *args, **kwargs):
        content = request.POST.get('content')
        if not content:
            return HttpResponseRedirect(self.get_success_url())
        else:
            return super(CreateMessage, self).post(request, *args, **kwargs)
        