#-*- encoding:utf-8 -*-  
  
import tornado.web  
import tornado.websocket  
import tornado.httpserver  
import tornado.ioloop  
import subprocess
from docker import Client
import time
import socket
from tornado import gen
import socket
import sys
import threading
import Queue
import requests
import json

reload(sys)
sys.setdefaultencoding('utf8')

class MyThread(threading.Thread):  
    def __init__(self,id,channel):  
        threading.Thread.__init__(self)  
        self.channel=channel
    def run(self):  
        while True:    
            try:
                data = self.channel.sock.recv(512)
                if not data:
                    break
                print data
                data_json={"data":data}
                self.channel.write_message(json.dumps(data_json))
            except Exception,ex:
                try:
                    data2=unicode(data, errors='replace')
                    data_json={"data":data2}
                    self.channel.write_message(data_json)
                except Exception,ex:
                    data_json={"data":'connect close;please refresh window'}
                    self.channel.write_message(data_json)
                    self.channel.sock.close()
                    break
        self.channel.sock.close()
        return False

##获取容器执行ID
def connect_containers(host,port,containers_id):
    headers={
        "Content-Type":"application/json"
    }
    data=json.dumps({
      "AttachStdin": True,
      "AttachStdout": True,
      "AttachStderr": True,
      "Cmd": ["/bin/bash"],
      "Privileged": True,
      "Tty": True
    })
    status={"status":True,"response":""}
    try:
        url='http://%s:%s/v1.24/containers/%s/exec'%(host,str(port),containers_id)
        result=requests.post(url, data=data,headers=headers)
        result_obj=result.text.replace("\n","")
        result_json=json.loads(result_obj)
        id=result_json["Id"]
        status.update({"response":id})
    except Exception,ex:
        response=u'%s 获取容器任务ID失败,请检查主机/端口/容器ID是否正确...'%(str(ex))
        status.update({"status":False,"response":response})
    return status
##重置容器窗口大小
def resize_containers(host,port,containers_id,width,height):
    headers={
        "Content-Type":"text/plain"
    }
    try:
        url='http://%s:%s/v1.24/exec/%s/resize?h=%s&w=%s'%(host,str(port),containers_id,width,height)
        result=requests.post(url,data={},headers=headers)
    except Exception,ex:
        print str(ex)
    #data=json.dumps({})

class IndexPageHandler(tornado.web.RequestHandler):  
    def get(self):  
        self.render('index.html')  
  
class WebSocketHandler(tornado.websocket.WebSocketHandler):  
    def check_origin(self, origin):  
        return True  

    def open(self):
        status={"status":True,"response":""}
        try:
            ##获取参数
            args=self.request.arguments
            host=args["h"][0]
            port=int(args["p"][0])
            containers_id=args["containers_id"][0]
            rows=args["rows"][0]
            cols=args["cols"][0]
            ##获取容器ID
            connect_json=connect_containers(host,port,containers_id)
            id=connect_json["response"]

            if connect_json["status"]:
                ##成功
                response=connect_json["response"]
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((host, port))
                param_data = '{"Tty":true}'
                param_lenth = len(param_data)
                str="""POST /exec/%(id)s/start HTTP/1.1\r\nHost: %(host)s:%(port)s\r\nContent-Type: application/json\r\nContent-Length: %(param_lenth)s\r\n\r\n%(param_data)s"""%{"id":response,"host":host,"port":port,"param_lenth":param_lenth,"param_data":param_data}
                self.sock.send(str)
                resize_containers(host,port,id,rows,cols)
                t1=MyThread(999,self)
                t1.setDaemon(True)
                t1.start() 
            else:
                ##失败
                response=connect_json["response"]
                status.update({"status":False,"data":response})
                self.write_message(status)
        except Exception,ex:
            #print str(ex)
            response="%s 联接容器失败..."%(str(ex))
            status.update({"status":False,"data":response})
            self.write_message(status)

    def on_message(self, message):  
        try:
            self.sock.send(message.encode("utf8"))
        except Exception,ex:
            print str(ex)
        
    def on_close(self):  
        try:
            data_json=json.dumps({"data":"connect close , pleace refesh the window..."})         
            self.write_message(data_json)
            self.sock.close()
        except:
            pass
  
class Application(tornado.web.Application):  
    def __init__(self):  
        handlers = [  
            (r'/', IndexPageHandler),  
            (r'/ws', WebSocketHandler)  
        ]  
  
        settings = { "template_path": ".","static_path": "static"}  
        tornado.web.Application.__init__(self, handlers, **settings)  
  
if __name__ == '__main__':  
    ws_app = Application()  
    server = tornado.httpserver.HTTPServer(ws_app)  
    server.listen(8011)  
    tornado.ioloop.IOLoop.instance().start()  
''' 
python ws_app.py 
'''  
