#!/usr/bin/env python3
import stranger

import connexion
from gevent.pywsgi import WSGIServer
from flask import Flask, request
from twilio import twiml
from messages import messages


app = Flask(__name__)

@app.route('/sms', methods=['POST'])
def sms():
    message_body = request.form['Body']
    resp = twiml.Response()
    resp.message('Your message has been sent to the Upside Down')
    messages.add_message(message_body)
    return str(resp)

if __name__ == '__main__':
    stranger.start_client()
    app.run()

    # app = connexion.App(__name__, specification_dir='./swagger/')
    # app.add_api('swagger.yaml', arguments={'title': 'Stranger board'})
    http_server = WSGIServer(('', 8080), app)
    http_server.serve_forever()