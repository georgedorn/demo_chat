from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy

# Create your models here.
class Room(models.Model):
    name = models.CharField(max_length=64, unique=True)
    creator = models.ForeignKey(User)

    created = models.DateTimeField(auto_now_add=True)
    
    def get_absolute_url(self):
        return reverse_lazy('chatroom', kwargs={'room':self.name})
    
class Message(models.Model):
    room = models.ForeignKey(Room)
    user = models.ForeignKey(User)
    
    content = models.CharField(max_length=256) #somewhat arbitrary
    
    created = models.DateTimeField(auto_now_add=True)
    
    @staticmethod
    def get_for_room(room):
        """
        Helper for building a QS for messages in a room.
        """
        return Message.objects.filter(room=room)
    
    class Meta:
        ordering = ['-created'] 
    