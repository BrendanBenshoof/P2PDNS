#dummy network object untill we get a real one working
#import node
from node import Node_Info
import os
import hash_util
import message
import threading
import time
from globals import *

LAN_mode = True
from os.path import expanduser



def ensure_dir(f):
    try:
        os.mkdir(f)
        #print "made dir"
    except OSError:
        print "I think there is already dir"
        pass
    #print "done ensure"


class Dummy_Network():
    def __init__(self):
        self.mynode = None
        home = expanduser("~")
        self.root_mailbox_path = home + "/dummy_messages/"
        ensure_dir(self.root_mailbox_path)
        self.my_mailbox_path = self.root_mailbox_path
        self.callback = None

    def setup_node(self, mynode):
        self.mynode = mynode
        node_name = mynode.IPAddr+"_"+str(mynode.ctrlPort)
        self.my_mailbox_path = self.root_mailbox_path+node_name+"/"
        #print self.my_mailbox_path
        ensure_dir(self.my_mailbox_path)

    def send_message(self, msg, dest):
        node_name = dest.IPAddr+"_"+str(dest.ctrlPort)
        dest_path = self.root_mailbox_path+node_name+"/"+str(hash_util.generate_random_key())
        if msg.service == SERVICE_INTERNAL:
            pass
            #print "sending " + msg.get_content("type") + " to: " + dest_path
        outfile = file(dest_path,"w+")
        outfile.write(msg.serialize())
        outfile.close()

    def check_for_messages(self):
        while True:
            time.sleep(0.01)
            L = os.listdir(self.my_mailbox_path)
            ##print L
            for m in L:
                time.sleep(0.01)
                self.get_message(m)


    def get_message(self, msg_path):
        infile = file(self.my_mailbox_path+"/"+msg_path, "r")
        msg_data = infile.read()
        msg = message.Message.deserialize(msg_data)
        infile.close()
        try:
            os.remove(self.my_mailbox_path+"/"+msg_path)
        except OSError: 
            print "HERP DERP FAILED TO DELETE"
        tocall = lambda: self.callback(msg)
        t=threading.Thread(target=tocall)
        t.setDaemon(True)
        t.start()    
        

def start(mynode, callback):
    mynetwork = Dummy_Network()
    mynetwork.setup_node(mynode)
    mynetwork.callback = callback
    mynetwork.setup_node(mynode)
    t=threading.Thread(target=mynetwork.check_for_messages)
    t.setDaemon(True)
    t.start()
    return mynetwork

myip = None