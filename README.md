# Live chat with strangers application

Real time chat where you can:
- connect with random stranger that were in waiting room
- disconnect with him 
- send message in real time 

# With what is it build?
- HTML
- CSS
- JavaScript
- Python
- Django
- Channels - to handle websocket connections
- Heroku - hosting platform
- Redis server

# How chat works?
- user send message
- if user is paired with another user message reach redis server
- then server gets paired user channel name and send message content and type (sender,receiver)
- on frontend javascript handle message and display message type on chat log

# How selecting a random stranger works?
- when user enter room and if waiting room is empty he get waiting status 
- if in waiting room is user they get paired and can chat and waiting room become empty
