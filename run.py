#@title staging
#rayanfer32@gmail.com  
#ngrok_token = "1VqGhSE64irU4DUnhunk5VPwMMG_87vkCxwNrr1uykLYoUANG"

import os
if "ngrok" not in os.listdir():
  os.system("wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip -O ngrok.zip;unzip ngrok.zip > /dev/null")

import json,requests
#@title #FLASK SERVER
test_mode = True #@param {type:"boolean"}
# import socket
# print(socket.gethostbyname(socket.getfqdn(socket.gethostname())))

#load static files
#PENDING 


#!curl -s http://localhost:4040/api/tunnels | python3 -c \
#  "import sys, json; print(json.load(sys.stdin)['tunnels'][0]['public_url'])"


# SEND NEW URL TO UBIDOTS FOR PARSING
#requests.get("https://industrial.ubidots.com/api/v1.6/devices/colab/?token=BBFF-M7ILRHc7jaPB0QRbebTJP6T4zmQL2D&_method=post&ngport="+port)
DEVICE = "colab"
TOKEN = "BBFF-M7ILRHc7jaPB0QRbebTJP6T4zmQL2D"
url = "http://industrial.api.ubidots.com/api/v1.6/devices/{}".format(DEVICE)
headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}

def send_payload(payload):
  requests.post(url, headers=headers, json=payload)

def get_tunnel():
  try:
    # print("creating a tunnel over ngrok")
    portfwd = "6006"
    os.system('./ngrok http '+portfwd+' &')
    # get_ipython().system_raw('./ngrok http '+portfwd+' &')
    tunnel_list = requests.get("http://localhost:4040/api/tunnels").json()
    # print(tunnel_list)
    new_tunnel = tunnel_list['tunnels'][0]['public_url']
    print(new_tunnel)
    if new_tunnel is not None:
      send_payload({"flask1":{"value":1,"context":{"tunnel":new_tunnel}}})
    return new_tunnel
  except:
    # print("retry ...")
    get_tunnel()

tun = get_tunnel()
print(tun)

from tasks import *
from flask import Flask,request
import time
app = Flask(__name__,static_folder="/content/",root_path='/content/')

#redis 
import redis
from rq import Queue
r = redis.Redis()
q = Queue(connection=r)


# @app.route("/")
# def hello():
#     return app.send_static_file("web/index.html")

@app.route("/",methods = ['POST', 'GET'])
def proc():
  try:
    if(method == 'POST'):
      song = request.form['song']
      mail = request.form['mail']
      print("request from :",mail,"song :",song)
      import ytdl
      ytdl.dl(song)
      return "processing:"+song
  except:
    return "No song name"
  
  #add to task queue and return task-id
  
  # return app.send_static_file("web/proc.html")


@app.route("/task")
def index():
    if request.args.get("n"):
        job = q.enqueue(background_task, request.args.get("n"))
        return f"Task ({job.id}) added to queue at {job.enqueued_at}"
    return "No value for count provided"

@app.route('/login',methods = ['POST', 'GET'])
def login():
  if(request.method == 'POST'):
    user = request.form['nm']
    passw = request.form['pass']
  if(user == 'admin' and passw == 'admin123'):
    return redirect(url_for('success',name = user))
  else:
    return app.send_static_file('./login.html')

if(test_mode): 
  app.run(host = '0.0.0.0',port = 6006) 
#  !export FLASK_APP=run.py;export FLASK_ENV=development;flask run
else:
  import threading
  threading.Thread(target=app.run, kwargs={'host':'0.0.0.0','port':6006}).start() 

