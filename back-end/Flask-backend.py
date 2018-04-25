import csv
from flask import Flask
from flask_socketio import SocketIO, emit
from StringIO import StringIO
app = Flask(__name__)
socketio = SocketIO(app)
category_dict = {0: 'Harware', 1: 'Software', 2: 'General', 3: 'Other'}


@socketio.on('analyze')
def handle_message(message):
    csv_data = message['data']
    f = StringIO(csv_data)
    reader = csv.reader(f)
    # csv_arrary = list(reader)
    for a in reader:
        print a
    emit('result', {'data': 'fuck you buddy'})


if __name__ == '__main__':
    socketio.run(app)