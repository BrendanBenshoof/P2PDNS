#simpler networking solution
from SocketServer import *
import threading
import socket
import voronoinode as node
import message
from Queue import *
import time

CHUNKSIZE = 64



##stolen from http://code.activestate.com/recipes/574454-thread-pool-mixin-class-for-use-with-socketservert/
class ThreadPoolMixIn(ThreadingMixIn):
    '''
    use a thread pool instead of a new thread on every request
    '''
    allow_reuse_address = True  # seems to fix socket.error on server restart
    numThreads = 10
    def serve_forever(self):
        '''
        Handle one request at a time until doomsday.
        '''
        # set up the threadpool
        self.requests = Queue(self.numThreads)

        for x in range(self.numThreads):
            t = threading.Thread(target = self.process_request_thread)
            t.setDaemon(1)
            t.start()

        # server main loop
        while True:
            self.handle_request()
            
        self.server_close()

    
    def process_request_thread(self):
        '''
        obtain request from queue instead of directly from server socket
        '''
        while True:
            try:
                ThreadingMixIn.process_request_thread(self, *self.requests.get())
            except Exception:
                pass

    
    def handle_request(self):
        '''
        simply collect requests and put them on the queue for the workers.
        '''
        try:
            request, client_address = self.get_request()
        except socket.error:
            return
        except:
            print "BLARG"
        if self.verify_request(request, client_address):
            self.requests.put((request, client_address))

class ThreadedServer(ThreadPoolMixIn, TCPServer):
    pass


class NETWORK_SERVICE(object):
    def sender_loop(self):
            while True:
                try:
                    priority, dest, msg = self.tosend.get(True)
                    self.client_send(dest,msg)
                    self.tosend.task_done()
                except Exception:
                    pass

    def send_message(self,msg,dest):
        msg_pack = (msg.priority,dest,msg)
        self.tosend.put(msg_pack,True)
        

    def __init__(self,HOST="localhost",PORT=9000):
        # Create the server, binding to localhost on port 9999
        self.server = ThreadedServer((HOST, PORT), MyTCPHandler)
        self.tosend = PriorityQueue()
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        t = threading.Thread(target=self.server.serve_forever)
        t.daemon = True
        t.start()
        for i in range(0,10):
            t2 = t = threading.Thread(target=self.sender_loop)
            t2.daemon = True
            t2.start()

    def stop(self):
        self.server.shutdown()

    def update_messages_in_queue(self, failed_node):
        hold = []
        while not self.tosend.empty():
            temp = self.tosend.get()
            self.tosend.task_done()
            if temp[1] == failed_node:
                node.message_failed(temp[2],temp[1])
            else:
                hold.append(temp)
        for h in hold:
            self.tosend.put()

    def client_send(self, dest, msg):
        #print msg.service, msg.type, str(dest)
        HOST = dest.IPAddr
        PORT = dest.ctrlPort
        DATA = msg.serialize()
        ##print len(DATA)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2.0)
        try:
            # Connect to server and send data
            sock.connect((HOST, PORT))
            sock.send(DATA)
            sock.shutdown(1)
            ack = sock.recv(1)
        except socket.error:
            ##print e
            #sock.close()
            print "SOCKET ERROR", "Tried to send to ", HOST, ":",PORT
            node.message_failed(msg,dest)
            #self.update_messages_in_queue(dest)
        finally:
            #print ">",
            sock.close()
            ##print DATA[-20:],len(DATA)%8
            return True


class MyTCPHandler(BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def __init__(self, request, client_address, server):
        self.data = ""
        BaseRequestHandler.__init__(self, request, client_address, server)



    def handle(self):
        # self.request is the TCP socket connected to the client
        data = ""
        data0="0"
        while len(data0) > 0:
            ###print length
            data0 = self.request.recv(1024)
            data+=data0
        self.request.send("ack")
        #self.request.shutdown()
        self.request.close()

        msg = message.Message.deserialize(data)
        #print "]",
        node.handle_message(msg)


    def handle_error(self, request, client_address):
        print client_address,"tried to talk to me and failed"
