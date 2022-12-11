# Start with a basic flask app webpage.
from flask_socketio import SocketIO, emit
from flask import Flask, render_template, url_for, copy_current_request_context, request
from random import random
from time import sleep
from threading import Thread, Event
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import pandas as pd
import os

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'bum!'
#turn the flask app into a socketio app
socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)
# basedir = os.path.abspath(os.path.dirname(__file__))

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'CPUload.db')
# #app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#
# db = SQLAlchemy(app)

# #random number Generator Thread
thread = Thread()
thread_stop_event = Event()

def randomNumberGenerator():
    """
    Generate a random number every 2 seconds and emit to a socketio instance (broadcast)
    Ideally to be run in a separate thread?
    """
    #infinite loop of magical random numbers
    print("Making random numbers")
    while not thread_stop_event.is_set():
        number = round(random()*10, 3)
        print(number)
        socketio.emit('newnumber', {'number': number}, namespace='/test')
        socketio.sleep(2)

def get_db_connection():
    conn = sqlite3.connect('CPUload.db')
    conn.row_factory = sqlite3.Row
    return conn

# def getData():
#     conn = sqlite3.connect('http://127.0.0.1:5000/CPUload.db')
#     #curs = conn.cursor()
#     df = pd.read_sql("SELECT * FROM cpulog", conn)
#
#     # for row in curs.execute("SELECT * FROM cpulog"):
#     #     print("DATA:", row)
#     conn.close()
#     return df

# @app.route('/')
# def index():
#     conn = get_db_connection()
#     posts = conn.execute('SELECT * FROM posts').fetchall()
#     conn.close()
#     return render_template('index.html', posts=posts)


@app.route('/')
def index():
    conn = get_db_connection()
    get_df = conn.execute('SELECT * FROM cpulog').fetchall()
    conn.close()

    return render_template('graphPage.html', get_df=get_df)
# @app.route('/')
# def index():
#     #only by sending this page first will the client be connected to the socketio instance
#     return render_template('graphPage.html')

@socketio.on('connect', namespace='/test')
def test_connect():
    # need visibility of the global thread object
    global thread
    print('Client connected')

    #Start the random number generator thread only if the thread has not been started before.
    if not thread.is_alive():
        print("Starting Thread")
        thread = socketio.start_background_task(randomNumberGenerator)

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app)
    # app.run(host='0.0.0.0', port=80, debug=False)



# # import datetime
# # from flask import Flask, render_template
# # app = Flask(__name__)
# # @app.route('/')
# # def hello():
# #     return render_template('graphPage.html', utc_dt=datetime.datetime.utcnow())
#
# from flask import Flask, render_template, request
# app = Flask(__name__)
# import sqlite3
# import pandas as pd
#
# # Retrieve data from database
# def getData():
#     conn = sqlite3.connect('CPUload.db')
#     # curs = conn.cursor()
#     df = pd.read_sql("SELECT * FROM cpulog", conn)
#
#     # for row in curs.execute("SELECT * FROM cpulog"):
#     #     print("DATA:", row)
#     conn.close()
#     return df
#
#
# # main route
# @app.route("/")
# def index():
#     get_df = getData()
#     print("************\n", get_df)
#
#     return render_template('graphPage.html', get_df=get_df)
#
#
# if __name__ == "__main__":
#     app.run(host='0.0.0.0', port=80, debug=False)