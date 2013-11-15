#dist_webserver

import SimpleHTTPServer
import SocketServer
import BaseHTTPServer
import time

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn

import hash_util

import threading
from service import Service
from message import Message

import cgi

from globals import *

PORT = 9080

class Open_request(object):
    def __init__(self, myservice, filename):
        self.myservice = myservice
        self.filename = filename
        self.hashloc = hash_util.hash_str(filename)
        self.contents = ""
        self.waiting = True
        request = Database_Message(myservice.owner, self.hashloc)
        myservice.send_message(request,None)
    
    def get_file(self,blocking=True):
        if not blocking:
            if not self.waiting:
                return self.contents
            else:
                return None
        else:
            while(self.waiting):
                time.sleep(0.1)
            return self.contents
    
    def update_file(self,contents):
        self.contents = contents
        self.waiting = False

WEBSERV = None

class WEBSERVICE(Service):
    """docstring for Database"""
    def __init__(self, db):
        global WEBSERV
        self.db = db
        WEBSERV = self
        super(WEBSERVICE, self).__init__()
        self.service_id = "WEBSERVICE"
        self.open_requests = {}
        self.webserver = threading.Thread(target = start_web)
        self.webserver.start()

    def attach(self, owner, callback):
        """Called when the service is attached to the node"""
        """Should return the ID that the node will see on messages to pass it"""
        self.callback = callback
        self.owner = owner
        return self.service_id

    def handle_message(self, msg):
        """This function is called whenever the node recives a message bound for this service"""
        """Return True if message is handled correctly
        Return False if things go horribly wrong
        """
        #if not msg.service == self.service_id:
        #    raise "Mismatched service recipient for message."
        if msg.type == "RESP":
            key = msg.get_content("destkey")
            file_contents = msg.get_content("file_contents")
            self.open_requests[key].update_file(file_contents)
        return msg.service == self.service_id

    def http_get(self,path):
        key = hash_util.hash_str(path)
        self.open_requests[key] = Open_request(self, path)
        return self.open_requests[key].get_file(blocking=True)
        
    def http_post(self,path,data):
        self.db.put_record(path,data)
    
    def attach_to_console(self):
        ### return a list of command-strings
        return None

    def handle_command(self, comand_st, arg_str):
        ### one of your commands got typed in
        return None

    def send_message(self, msg, dest):
        msg.priority=self.priority
        self.callback(msg, dest)

    def change_in_responsibility(self,new_pred_key, my_key):
        pass #this is called when a new, closer predicessor is found and we need to re-allocate
            #responsibilties


class Database_Message(Message):
    def __init__(self, origin_node, destination_key, Response_service="WEBSERVICE", file_type="GET"):
        Message.__init__(self, SERVICE_SHELVER, file_type)
        self.origin_node = origin_node
        self.destination_key = destination_key
        self.add_content("service",Response_service)
        self.reply_to = origin_node




class HashwebHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
    def do_GET(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        print s.path
        msg = WEBSERV.http_get(s.path)
        s.wfile.write(msg)
    def do_POST(self):
        # Parse the form data posted
        form = cgi.FieldStorage(
        fp=self.rfile, 
        headers=self.headers,
        environ={'REQUEST_METHOD':'POST',
        'CONTENT_TYPE':self.headers['Content-Type'],
        })

        # Begin the response
        self.send_response(200)
        self.end_headers()
        # Echo back information about what was posted in the form
        data = ""
        loc = ""
        for field in form.keys():
            field_item = form[field]
            if field_item.filename:
                # The field contains an uploaded file
                return
            else:
                # Regular form value
                if field == "data":
                    data = form[field].value
                if field == "path":
                    loc = form[field].value
        WEBSERV.http_post(loc,data)
        return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

def start_web():
    server = ThreadedHTTPServer(('', PORT), HashwebHandler)
    print 'Starting server, use <Ctrl-C> to stop'
    server.serve_forever()
