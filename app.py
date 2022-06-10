import pickle
import os
from flask import Flask, request, jsonify, make_response
from urllib.parse import urlparse
from urllib.parse import parse_qs
from urllib.parse import urlencode

app = Flask(__name__)

@app.route('/readInitiater', methods = ['POST', 'GET'])
def read_initiater():
  active_connections = pickle.load(open('active_connections.p','rb'))
  if len(active_connections)>0:
    sender = active_connections.pop(0)
    return sender
  else:
    return '<NONE>'

  
@app.route('/getValue', methods = ['POST', 'GET'])
def get_value():    
    body = request.get_json(silent=True)
    number = body['from']
    number_msg_dict = pickle.load(open('received_msgs.p','rb'))
    out_msg = '<NULL>'
    if number in number_msg_dict:
      if number_msg_dict[number]!='NULL':
        out_msg = number_msg_dict[number]
        number_msg_dict[number] = 'NULL'
        pickle.dump(number_msg_dict,open('received_msgs.p','wb'))
    return out_msg
  

@app.route('/webhook',methods = ['POST', 'GET'])
def decode_message():
    verify_token = 'helloworld'
    body = request.get_json(silent=True)
    print(body)
    if request.method == 'POST':
        try:            
            sender = body['entry'][0]['changes'][0]['value']['messages'][0]['from']
            msg_body = body['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']            
            
            number_msg_dict = pickle.load(open('received_msgs.p','rb'))
            active_connections = pickle.load(open('active_connections.p','rb'))
            
            if sender not in active_connections:              
              active_connections.add(sender)
              pickle.dump(active_connections, open('active_connections.p','wb'))
              
            number_msg_dict[sender] = msg_body
            pickle.dump(number_msg_dict,open('received_msgs.p','wb'))            
            
            data = {'message': 'MSG RECEIVED', 'code': 'SUCCESS'}
            return make_response(jsonify(data), 200)
        except:
            data = {'message': 'MSG NOT FOUND', 'code': 'UNSUCCESS'}
            return make_response(jsonify(data), 404)
        
    elif request.method == 'GET': 
        o = urlparse(request.url)
        query = parse_qs(o.query)
        mode = query.get('hub.mode')[0]
        token = query.get('hub.verify_token')[0]
        challenge = query.get('hub.challenge')[0]
        
        if mode == "subscribe" and token == verify_token:
            print("WEBHOOK_VERIFIED")
            return make_response(challenge, 200)
        else:
            data = {'message': 'MSG NOT FOUND', 'code': 'UNSUCCESS'}
            return make_response(data, 403)
        
if __name__ == '__main__':    
    app.run() 
