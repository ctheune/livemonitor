from .haproxy import HAProxy
from flask import Flask, render_template, make_response, request
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
import json
import logging
import random
import threading
import time

logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return make_response()


@app.route('/data')
def data():
    if 'wsgi.websocket' in request.environ:
        data_websocket(request.environ['wsgi.websocket'])
        return
    return data_one()


def data_one():
    data =  {}
    for source in sources:
        for name, value, time in source.metrics():
            data[name] = dict(value=value, time=time)
    return json.dumps(data)


def data_websocket(ws):
    while True:
        data = data_one()
        ws.send(data)
        time.sleep(0.1)


sources = []


def update():
    while True:
        for source in sources:
            source.update()
        time.sleep(0.1)


def main():
    sources.append(HAProxy())
    app.debug = True
    update_thread = threading.Thread(target=update)
    update_thread.setDaemon(True)
    update_thread.start()
    server = WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()
