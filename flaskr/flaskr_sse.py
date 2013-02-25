import sqlite3
from flask import Flask, request, Response, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing

import gevent
import gevent.monkey
from gevent.pywsgi import WSGIServer
import redis
gevent.monkey.patch_all()

#config block
DATABASE='/tmp/flaskr.db'
DEBUG=True
SECRET_KEY='development key'
USERNAME='admin'
PASSWORD='default'

app=Flask(__name__)
app.config.from_object(__name__) #loads config from file referenced by __name__, ie this file
# better - app.config.from_envvar('FLASKR_SETTINGS', silent=True), where FLASKR_SETTINGS is env variable
#  containing name of config file

client = redis.StrictRedis()

    
@app.route('/')
def page():
    return render_template('sse.html')
    
#SSE stuff
def event_stream():
    count = 0
    while True:
        gevent.sleep(5)
        yield 'data: %s\n\n' % count
        count += 1

def redis_stream( pubsub ):
    for message in pubsub.listen():
        yield 'data: %s\n\n' % message['data']
        
@app.route('/my_event_source')
def sse_request():
    return Response(event_stream(), mimetype="text/event-stream")

@app.route('/redis_events')
def redis_sse():
    pubsub = client.pubsub()
    pubsub.subscribe('warnings')
    return Response( redis_stream(pubsub), mimetype="text/event-stream")

if __name__ == "__main__":
    http_server = WSGIServer(('192.168.0.3', 8001), app)
    http_server.serve_forever()