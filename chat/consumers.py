# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import random
from channels.layers import get_channel_layer
# from . user_functions import waiting_for_stranger

active_users = []

paired_users = {}

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return random.randint(range_start, range_end)


class UserInfos():
    def send_connected_info(self):
        async_to_sync(self.channel_layer.send)(
        self.channel_name,
        {
            'type': 'connected_with_stranger',
        })
        async_to_sync(self.channel_layer.send)(
        paired_users[self.channel_name],
        {
            'type': 'connected_with_stranger',
        })


    def connect_with_user(self):

        if len(active_users) < 1:
            active_users.append(self.channel_name)

        elif len(active_users) >= 1:
            stranger = active_users[0]
            active_users.remove(stranger)

            paired_users[stranger] = self.channel_name
            paired_users[self.channel_name] = stranger
            UserInfos.send_connected_info(self)


    def disconnect_with_stranger(self):
        stranger = paired_users[self.channel_name]
        # Send stranger info that you disconnected
        async_to_sync(self.channel_layer.send)(
            stranger,
            {
                'type': 'disconnected_with_stranger',
            }
        )

        del paired_users[stranger]
        del paired_users[self.channel_name]


    def send_typing_info(self):
        user = self.scope['session']['seed']

        # Send typing info to connected user
        async_to_sync(self.channel_layer.send)(
            paired_users[self.channel_name],
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
            paired_users[self.channel_name],
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

    
