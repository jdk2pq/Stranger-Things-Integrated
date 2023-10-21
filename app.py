#!/usr/bin/env python3
import stranger

import connexion
from gevent.pywsgi import WSGIServer
from flask import Flask, request
from twilio import twiml


app = Flask(__name__)

if __name__ == '__main__':
    stranger.start_client()

    # app = connexion.App(__name__, specification_dir='./swagger/')
    # app.add_api('swagger.yaml', arguments={'title': 'Stranger board'})
    app.run()
    http_server = WSGIServer(('', 8080), app)
    http_server.serve_forever()

@app.route('/sms', methods=['POST'])
def sms():
    number = request.form['From']
    message_body = request.form['Body']
    resp = twiml.Response()
    resp.message('Hello {}, you said: {}'.format(number, message_body))
    return str(resp)