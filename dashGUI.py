import dash
from dash import html, dcc
from dash.dependencies import Input, Output
from flask import Flask
import sqlite3
import os

basedir = os.path.abspath(os.path.dirname(__file__))

fpp = Flask(__name__)
fpp.config['SECRET_KEY'] = 'secret!'
fpp.config['DEBUG'] = True

fpp.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'CPUload.db')

figure = dict(data=[{'x': [], 'y': []}],
              layout=dict(title='CPU Load Level',
                          yaxis=dict(range=[0, 100], title='Процент загрузки ЦП'),
                          xaxis=dict(title='Время')
                          )
              )

app = dash.Dash(__name__, update_title=None)  # remove "Updating..." from title
app.layout = html.Div([dcc.Graph(id='graph', figure=figure,
                                 style={'height': '90vh'}  # graph is 90% of the height of the browser's viewport
                                 ),
                       dcc.Interval(id="interval")])


@app.callback(Output('graph', 'extendData'), [Input('interval', 'n_intervals')])
def update_data(n_intervals):
    conn = sqlite3.connect('CPUload.db')
    conn.row_factory = sqlite3.Row
    results = conn.execute('SELECT * FROM cpulog').fetchall()
    results = [tuple(row) for row in results]

    conn.close()

    #print("-------------", dict(x=[[results[-1][0]]], y=[[results[-1][1]]]), "--------------------")
    # tuple is (dict of new data, target trace index, number of points to keep)
    return dict(x=[[results[-1][0]]], y=[[results[-1][1]]]), [0], 50


if __name__ == '__main__':
    app.run_server()
