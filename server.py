import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.escape
import datetime
import json
import rospy # Python client library for ROS
from std_msgs.msg import String

import threading

# define global json variable
json_data = {}

clients = []

tornado_ioloop = object()


def spin_ros():
    rospy.spin()

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    connections = set()
    pub = object()
    # make the var connections to global variable

    def open(self):
        self.connections.add(self)
        clients.append(self)    
        self.pub = rospy.Publisher("chatter2", String, queue_size=10)
        self.update_time()

    def update_time(self):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        response = {"time": now}
        # print(self)
        self.write_message(json.dumps(response))
        # rospy.Rate()

        # rospy.wait_for_message("chatter", String, timeout=0.01)
        tornado.ioloop.IOLoop.current().add_timeout(datetime.timedelta(seconds=0.01), self.update_time)

    def on_message(self, message):
        # print(self)
        # print(message)
        try:
            data = json.loads(message)
            mode = data.get("mode")
            if mode == 2:
                text = data.get("text")
                response = {"input_text": text}
                # self.pub.publish(text)
                # print(response)
                self.write_message(json.dumps(response))
            
            elif mode == 3:
                text = data.get("text")
                response = {"input_text": text}
                self.pub.publish(text)

            else:
                response = {"error": "Invalid mode"}
                self.write_message(json.dumps(response))
        except Exception as e:
            print(f"Error: {e}")

    def on_close(self):
        self.connections.remove(self)
        clients.remove(self)
    
    @classmethod
    def send_message(cls, message):
        global tornado_ioloop
        for wbs in cls.connections:
            # print(wbs)
            # tornado.ioloop.IOLoop.current().add_callback(wbs.on_message, message)

            # tornado.ioloop.IOLoop.. 
            
            tornado_ioloop.add_callback(wbs.on_message, message)
        # print(cls)
        # print(message)
            

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/websocket", WebSocketHandler),
        ]
        settings = {
            "template_path": ".",
            "static_path": ".",
        }
        super(Application, self).__init__(handlers, **settings)

def callback(data):
    # print String data to console
    # print(data.data)

    # update global json variable
    global json_data

    # update json variable with new data with mode:2 and input_text: data.data
    json_data = {"mode": 2, "text": data.data}

    # send json data to all clients
    # for conn in WebSocketHandler.connections:
        # conn.write_message(json.dumps(json_data))

    WebSocketHandler.send_message(json.dumps(json_data))
    # if len(clients) > 0:    
    #     clients[0].write_message(json.dumps(json_data))

    
    # print(json_data)



if __name__ == "__main__":
    # global tornado_ioloop
    
    app = Application()
    app.listen(8888)
    # initialize ros node with name 'subscriber' and add subscriber to topic 'chatter'
    rospy.init_node('subscriber', anonymous=True)
    rospy.Subscriber("chatter", String, callback)

    # spin_thread = threading.Thread(target=spin_ros)
    # spin_thread.start()

    tornado_ioloop = tornado.ioloop.IOLoop.current()
    tornado_ioloop.start()
    # tornado.ioloop.IOLoop.current().start()

