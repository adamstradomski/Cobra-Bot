from flask import Flask
from threading import Thread
#
#  This is a simple Web Server to keep aliave bot application live in replit.com 
#
app = Flask('')

@app.route('/')
def home():
  return "Hello!"

def run():
  app.run(host='0.0.0.0',port=8080)

# Run webserver on a separate thread 
def keep_alive():
  t = Thread(target=run)
  t.start()