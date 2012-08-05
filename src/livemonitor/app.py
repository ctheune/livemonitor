from flask import Flask, render_template, make_response, request
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from repoze.debug.responselogger import ResponseLoggingMiddleware
import gevent
import json
import livemonitor.haproxy
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



##### UI configuration

charts = []
@app.route('/charts')
def get_charts():
    return json.dumps([
        ["RequestRate", "ErrorResponses", "Error4xx", "Error5xx"],
        ["Health"]])


##### Data streaming

@app.route('/data')
def data():
    if 'wsgi.websocket' in request.environ:
        data_websocket(request.environ['wsgi.websocket'])
        return
    return data_one()


def data_one():
    data =  {}
    for measure in measures:
        data[measure.__class__.__name__] = dict(
            value=measure.value, time=int(measure.timestamp*1000))
    return json.dumps(data)


def data_websocket(ws):
    while True:
        data = data_one()
        ws.send(data)
        gevent.sleep(0.1)


sources = []
measures = []

def update():
    while True:
        for source in sources:
            source.update()
        for measure in measures:
            measure.update()
        time.sleep(0.1)


def main():
    haproxy = livemonitor.haproxy.configure()
    sources.append(haproxy[0])
    measures.extend(haproxy[1])

    update_thread = threading.Thread(target=update)
    update_thread.setDaemon(True)
    update_thread.start()

    logging.basicConfig(level=logging.DEBUG)

    pipeline = ResponseLoggingMiddleware(
        app,
        max_bodylen=3072,
        keep=100,
        verbose_logger=logging.getLogger('verbose'),
        trace_logger=logging.getLogger('trace'))
    server = WSGIServer(('', 5000), pipeline, handler_class=WebSocketHandler)
    server.serve_forever()
