from flask import Flask, request, session, redirect, url_for, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
import hashlib

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# User database (replace with your own database implementation)
users = {
    'ryadahlke': hashlib.sha256('rd#37727'.encode()).hexdigest(),
    'test_user': hashlib.sha256('flask_test'.encode()).hexdigest(),
    'uk_tester': hashlib.sha256('uk_tester_password'.encode()).hexdigest()
}

# Login page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        if username in users and password == users[username]:
            session['username'] = username
            return redirect(url_for('chat'))
        else:
            return render_template('login.html', error='Invalid username or password')
    else:
        return render_template('login.html')

# Chatroom page
@app.route('/chat')
def chat():
    if 'username' in session:
        return render_template('chat.html', username=session['username'])
    else:
        return redirect(url_for('login'))

# SocketIO event handlers
@socketio.on('join')
def on_join(data):
    username = session['username']
    room = data['room']
    join_room(room)
    emit('status', {'msg': username + ' has entered the room.'}, room=room)

@socketio.on('leave')
def on_leave(data):
    username = session['username']
    room = data['room']
    leave_room(room)
    emit('status', {'msg': username + ' has left the room.'}, room=room)

@socketio.on('message')
def on_message(data):
    username = session['username']
    room = data['room']
    emit('message', {'username': username, 'msg': data['msg']}, room=room)

if __name__ == '__main__':
    socketio.run(app, host='localhost', port=25565)
