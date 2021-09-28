# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import random
from channels.layers import get_channel_layer

active_users = []

paired_users = {

}

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return random.randint(range_start, range_end)

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        self.scope['session']['seed'] = random_with_N_digits(8)
        
        if len(active_users) < 1:
            print('added')
            active_users.append(self.channel_name)
        else:
            print('paired')
            stranger = active_users[0]
            active_users.remove(stranger)
            paired_users[stranger] = self.channel_name
            paired_users[self.channel_name] = stranger
            print(paired_users)


        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()







    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        channel_layer = get_channel_layer()
        print(self.channel_layer)

        try:
            typing = text_data_json['typing']
            user = self.scope['session']['seed']

            # Send typing info
            async_to_sync(self.channel_layer.send)(
                paired_users[self.channel_name],
                {
                    'type': 'typing',
                    'message': user,
                }
            )
            

        except:
            message = text_data_json['message']
            user = self.scope['session']['seed']
            message = str(user) + message

            # Send message to room group
            async_to_sync(self.channel_layer.send)(
                paired_users[self.channel_name],
                {
                    'type': 'chat_message',
                    'message': message,
                }
            )
            async_to_sync(self.channel_layer.send)(
                self.channel_name,
                {
                    'type': 'chat_message',
                    'message': message,
                }
            )

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