import csv
import random
from flask import Flask
from flask_socketio import SocketIO, emit
from StringIO import StringIO
app = Flask(__name__)
socketio = SocketIO(app)
category_dict = {0: 'Harware', 1: 'Software', 2: 'General', 3: 'Other'}


@socketio.on('analyze')
def handle_message(message):
    csv_data = message['data']
    model = message['model']
    result = []
    print model
    f = StringIO(csv_data)
    reader = csv.reader(f)
    csv_array = list(reader)
    csv_array.pop(0)
    # random array
    if '90' in model:
        base = 91
    elif '180' in model:
        base = 89
    else:
        base = 82
    for data in csv_array:
        # temp = [#ID, #Region, #MELD-Score, #Survival Rate]
        temp = [data[0], data[15], data[24], (0.0 + random.randrange(-20, 20)) / 10 + base]
        result.append(temp)
    for a in reader:
        print a
    emit('result', {'data': result, 'model': model})


if __name__ == '__main__':
    socketio.run(app)