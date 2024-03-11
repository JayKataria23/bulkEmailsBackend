from flask import Flask
from flask_cors import CORS
from flask import request
import smtplib
from PIL import Image
from email.message import EmailMessage
from base64 import b64decode
import os
from datetime import datetime
from flask import g

app=Flask(__name__)
CORS(app)
@app.route("/")
def welcome():
    return "Hello World!"

@app.before_request
def start_timer():
    print("start",datetime.now())

@app.after_request
def log_time(response):
    print("end",datetime.now())
    return response

@app.route("/sendMail", methods=["POST"])
def sendMail():
    data=request.get_json()
    sender=str(data['email'])
    password=str(data['password'])
    msg = EmailMessage()

    msg['Subject'] = str(data["subject"])
    msg['From'] = sender

    msg.set_content(str(data["body"]))

    msg.add_alternative(str(data["html"]), subtype='html')

    if data['attachments']:
        att = data['attachments']
        for x in att:
            bytes = b64decode(x['uri'].split(",")[1], validate=True)
            f = open(x['name'], 'wb')
            f.write(bytes)
            f.close()
            mime_type, mime_subtype = x['mimeType'].split('/', 1)
            with open(x['name'], 'rb') as f:
                msg.add_attachment(f.read(), maintype=mime_type, subtype=mime_subtype,filename=x['name'])
            os.remove(x['name'])

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender, password)
        for to in data["csv"].split()[1:]:
            msg['To'] = to
            smtp.send_message(msg)
            del msg["To"]

    return "Email Sent"