# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import random
from channels.layers import get_channel_layer

from . models import PairedUser, ActiveUser
# from . user_functions import waiting_for_stranger



def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return random.randint(range_start, range_end)


class UserInfos():

    def save_paired_user(user, stranger):
        User = PairedUser()
        User.user_id = user
        User.stranger_id = stranger
        User.save()
        # stranger
        Stranger = PairedUser()
        Stranger.user_id = stranger
        Stranger.stranger_id = user
        Stranger.save()

    def delete_paired_user(user, stranger):
        User = PairedUser.objects.get(user_id=user)
        User.delete()
        # stranger
        Stranger = PairedUser.objects.get(user_id=stranger)
        Stranger.delete()

    def save_active_user(user):
        User = ActiveUser()
        User.user_id = user
        User.save()

    def delete_active_user(user):
        User = ActiveUser.objects.get(user_id=user)
        User.delete()


    def send_user_number(self):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type':'display_number_of_users'
            })

    def send_connected_info(self):
        async_to_sync(self.channel_layer.send)(
        self.channel_name,
        {
            'type': 'connected_with_stranger',
        })
        async_to_sync(self.channel_layer.send)(
        PairedUser.objects.get(user_id=self.channel_name).stranger_id,
        {
            'type': 'connected_with_stranger',
        })


    def connect_with_user(self):

        if len(ActiveUser.objects.all()) < 1:
            # Save waiting user to database
            UserInfos.save_active_user(self.channel_name)
            
        elif len(ActiveUser.objects.all()) >= 1 and self.channel_name not in ActiveUser.objects.all():
            # get active user from database and delete him
            stranger = ActiveUser.objects.first().user_id
            UserInfos.delete_active_user(stranger)
            # save connected pair to database
            UserInfos.save_paired_user(self.channel_name, stranger)
            # Send info that users are connected
            UserInfos.send_connected_info(self)
          


    def disconnect_with_stranger(self):

        try:
            # if user has pair
            stranger = PairedUser.objects.get(user_id=self.channel_name).stranger_id
            # Send stranger info that you disconnected
            async_to_sync(self.channel_layer.send)(
                stranger,
                {
                    'type': 'disconnected_with_stranger',
                }
            )
            
            # delete disconnected pair from database
            UserInfos.delete_paired_user(self.channel_name, stranger)

        except:
            #if user was in waiting room
            UserInfos.delete_active_user(self.channel_name)


    def send_typing_info(self):
        user = self.scope['session']['seed']

        # Send typing info to connected user
        async_to_sync(self.channel_layer.send)(
            PairedUser.objects.get(user_id=self.channel_name).stranger_id,
            {
                'type': 'typing',
                'message': user,
            }
        )
        # Send typing info to yourself
        async_to_sync(self.channel_layer.send)(
            self.channel_name,
            {
                'type': 'typing',
                'message': user,
            }
        )

    def send_user_message(self, text_data_json):
        message = text_data_json['message']
        user = self.scope['session']['seed']
        message = str(user) + message

        # Send message to connected user
        async_to_sync(self.channel_layer.send)(
            PairedUser.objects.get(user_id=self.channel_name).stranger_id,
            {
                'type': 'chat_message',
                'message': message,
            }
        )
        # Send message to yourself
        async_to_sync(self.channel_layer.send)(
            self.channel_name,
            {
                'type': 'chat_message',
                'message': message,
            }
        )




class ChatConsumer(WebsocketConsumer):
    number_of_users = 0
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        self.scope['session']['seed'] = random_with_N_digits(8)
    
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

        #if join room connect with stranger
        UserInfos.connect_with_user(self)

        # send user number
        UserInfos.send_user_number(self)
        



    def disconnect(self, close_code):
        #clear database
        paired_users = {}
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )


    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)

        try:
            if text_data_json['action'] == 'typing':
                #send typing info
               UserInfos.send_typing_info(self)
            if text_data_json['action'] == 'leave':
                UserInfos.disconnect_with_stranger(self)
            if text_data_json['action'] == 'connect_new':
                UserInfos.connect_with_user(self)
            
            
        except:
            # Send user message
            UserInfos.send_user_message(self, text_data_json)



    # Receive message from room group
    def chat_message(self, event):

        sender = event['message'][0:8]
        message = event['message'][8:]

        if self.scope['session']['seed'] == int(sender):
            message_type = 'sender'
        else:
            message_type = 'receiver'

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message_type': message_type,
            'message': message
        }))


    # Display if user is typing
    def typing(self, event):

        if self.scope['session']['seed'] != int(event['message']):
            # Display that user is typing
            self.send(text_data=json.dumps({
                'message_type': 'typing',
                'message': True
            }))




    def connected_with_stranger(self, event):
        self.send(text_data=json.dumps({
            'message_type': 'connected_with_stranger',
        }))

    def disconnected_with_stranger(self, event):
        self.send(text_data=json.dumps({
            'message_type': 'disconnected_with_stranger',
        }))

    
    def display_number_of_users(self, event):
        print(event)
