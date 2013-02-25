import sqlite3
from flask import Flask, request, Response, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing

import gevent
import gevent.monkey
from gevent.pywsgi import WSGIServer
import redis
gevent.monkey.patch_all()

#config block
DEBUG=True

app=Flask(__name__)
app.config.from_object(__name__)

client = redis.StrictRedis()

    
@app.route('/')
def page():
    return render_template('sse.html')
    
#SSE stuff
def redis_stream( pubsub ):
    for message in pubsub.listen():
        yield 'data: %s\n\n' % message['data']
        
@app.route('/redis_events')
def redis_sse():
    pubsub = client.pubsub()
    pubsub.subscribe('warnings')
    return Response( redis_stream(pubsub), mimetype="text/event-stream")

if __name__ == "__main__":
    http_server = WSGIServer(('127.0.0.1', 8001), app)
    http_server.serve_forever()