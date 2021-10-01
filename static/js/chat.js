const roomName = JSON.parse(document.getElementById('room-name').textContent);

// open websocket connection to server
let protocol = window.location.protocol == "https:" ? "wss" : "ws";
const chatSocket = new WebSocket(
    protocol + '://' +
    window.location.host +
    '/ws/' +
    roomName +
    '/'
);

// display typing info if user is typing
let show_typing_info = function () {
    let classname = document.querySelector('#typing_info').className

    if (classname == 'hide') {
        // if typing_info is hidden change class to show
        document.querySelector('#typing_info').className = 'show';
        document.querySelector('#typing_info').style.display = 'block';
        // Set timeout to one second
        typing_timeout = window.setTimeout(function () {
            document.querySelector('#typing_info').className = 'hide';
            document.querySelector('#typing_info').style.display = 'none';
        }, 1000);

    } else {
        // Clear existiong timeout
        window.clearTimeout(typing_timeout)
        // And set new one
        typing_timeout = window.setTimeout(function () {
            document.querySelector('#typing_info').className = 'hide';
            document.querySelector('#typing_info').style.display = 'none';
        }, 1000);
    }
}

// display waiting info on chat log
let display_waiting = function () {
    // disable textarea and buttons during waiting
    document.getElementById('chat-message-input').disabled = true;
    document.getElementById('leave-chat').disabled = true;
    document.getElementById('chat-message-submit').disabled = true;

    // display waiting info
    document.getElementById('user_info').innerHTML = 'Waiting for stranger...';

    // cleare chat log 
    document.querySelector('#chat-log').innerHTML = `
    <li id='user_info' class='user_info'>Waiting for stranger...</li>
    <li id='typing_info' class='hide' style='color: #ccc; display:none'>User Typing...</li>
    `;
}

let display_disconnect = function () {
    // change leave button to connect with new
    document.getElementById('leave-chat').innerHTML = 'Connect to new stranger'
    document.getElementById('leave-chat').name = 'connect_new'

    // create disconnect info
    let disconnect_info = document.createElement("li")
    disconnect_info.appendChild(document.createTextNode('Stranger disconnected'));
    disconnect_info.style.color = "red";
    document.querySelector('#chat-log').appendChild(disconnect_info);

    // disable input and submit
    document.getElementById('chat-message-input').disabled = true;
    document.getElementById('chat-message-submit').disabled = true;
}



let typing_timeout;
// handle messages from websocket
chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);

    if (data.message_type == 'typing') {
        // if message type is typing show typing message
        show_typing_info()
        // scroll to bottom of chat box
        let cont = document.getElementById('chat_box')
        cont.scrollTop = cont.scrollHeight;


    } else if (data.message_type == 'sender' || data.message_type == 'receiver') {
        // get message content and display it on chat log
        let typing_info = document.querySelector('#typing_info')
        let message = document.createElement("li")
        message.setAttribute("class", data.message_type);
        message.appendChild(document.createTextNode(data.message));
        document.querySelector('#chat-log').appendChild(message);
        // append typing info after new message and set display to none
        typing_info.style.display = 'none'
        document.querySelector('#chat-log').appendChild(typing_info);
        // scroll to bottom of chat box
        let cont = document.getElementById('chat_box')
        cont.scrollTop = cont.scrollHeight;


    } else if (data.message_type == 'connected_with_stranger') {
        // if connected with stranger change text and enable textarea
        document.getElementById('chat-message-input').disabled = false;
        document.getElementById('leave-chat').disabled = false;
        document.getElementById('chat-message-submit').disabled = false;
        document.getElementById('user_info').innerHTML = 'Connected with stranger';

    } else if (data.message_type == 'disconnected_with_stranger') {
        display_disconnect()
        // scroll to bottom of chat box
        let cont = document.getElementById('chat_box')
        cont.scrollTop = cont.scrollHeight;

    } else if (data.message_type == 'number_of_users') {
        // display number of online users
        number_of_users = data.number_of_users
        document.getElementById('users_number').innerHTML = number_of_users.toString() + ' online users'
    }
};

chatSocket.onclose = function (e) {
    console.error('Chat socket closed unexpectedly');
};

document.querySelector('#chat-message-input').focus();
document.querySelector('#chat-message-input').onkeyup = function (e) {
    if (e.keyCode === 13) { // enter, return
        document.querySelector('#chat-message-submit').click();
    } else { // different then enter

        chatSocket.send(JSON.stringify({
            'action': 'typing'
        }));
    }
};

// send message after clicking submit button
document.querySelector('#chat-message-submit').onclick = function (e) {
    const messageInputDom = document.querySelector('#chat-message-input');
    const message = messageInputDom.value;
    chatSocket.send(JSON.stringify({
        'message': message
    }));
    // update textarea value
    messageInputDom.value = '';
};

// leave chat after clicking button
document.querySelector('#leave-chat').onclick = (e) => {
    let type = e.target.name;

    if (type == 'leave') {
        // ensure if user wants to disconnect
        e.target.name = 'ensure'
        e.target.innerHTML = 'Are you sure?'

    } else if (type == 'ensure') {
        // if user disconnect chane button content to connect to new stranger
        e.target.name = 'connect_new'
        e.target.innerHTML = 'Connect to new stranger'
        // create disconnect info
        let disconnect_info = document.createElement("li")
        disconnect_info.appendChild(document.createTextNode('You disconnected with stranger'));
        disconnect_info.style.color = "red";
        document.querySelector('#chat-log').appendChild(disconnect_info);
        // Send websocket that user wants to disconnect with stranger
        chatSocket.send(JSON.stringify({
            'action': 'leave'
        }));

    } else if (type == 'connect_new') {
        e.target.name = 'leave'
        e.target.innerHTML = 'Leave'
        // Display waiting status
        display_waiting()
        // Send websocket that user wants to connect with user
        chatSocket.send(JSON.stringify({
            'action': 'connect_new'
        }));

    }
}

// on refersh disconnect
window.onbeforeunload = function (e) {
    // Send websocket that user wants to disconnect with stranger
    chatSocket.send(JSON.stringify({
        'action': 'leave'
    }));
}