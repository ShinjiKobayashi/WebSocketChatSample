# -*- coding=utf-8 -*-

from flask import Flask, request, render_template
from flask_sockets import Sockets
from werkzeug.exceptions import abort


app = Flask(__name__)
sockets = Sockets(app)
wslist = set()


@sockets.route('/echo')
def echo(ws):
    while True:
        msg = ws.receive()
        ws.send(msg)


@sockets.route('/chat')
def chat(ws):
    if not ws:
        abort(400)

    wslist.add(ws)
    print 'enter!', len(wslist)

    while True:
        msg = ws.receive()
        print "get message:", msg
        if msg is None:
            # msgがなければいなくなったと見なす
            break

        remove = set()
        for s in wslist:
            try:
                s.send(msg)
            except Exception:
                # sendに失敗したら居なくなったとみなす
                remove.add(s)

        for s in remove:
            wslist.remove(s)

    print 'exit!', len(wslist)


@app.route('/')
def hello_world():
    return render_template('chat_sample.html')


if __name__ == '__main__':
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()
