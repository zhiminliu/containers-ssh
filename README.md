# containers-ssh
# 环境?
# linux(python2.7) windows(无) mac(无)
# 需要安装的依赖库?
# pip install tornado ; pip install requests; pip install docker-py;
# 如何使用?
# cd containers-ssh && python ws_app.py
# 默认端口(8011)?
  vim containers-ssh/ws_app.py
  if __name__ == '__main__':  
    ws_app = Application()  
    server = tornado.httpserver.HTTPServer(ws_app)  
    server.listen(8011)  
    tornado.ioloop.IOLoop.instance().start() 
# 浏览器登录,输入容器的宿主机的IP,宿主机的docker通信端口,容器ID
