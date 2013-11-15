#pulled from Benjamin Evans's implementation "pyChordDHT"
### TODO ###
# Finish stabilization
# hash math - some indexes are wrong <- I think this is fixed
# if request times out - use backup node
# update request on node failure
# Not closing connection properly - why?
############
from hash_util import *
from socket import *
import time
from threading import *
import signal
import sys
import uuid
import copy
from optparse import OptionParser
import random
from message import *
#import dummy_network as
import globals
import Queue

import spacemath


# Debug variables
TEST_MODE = False   #duh
VERBOSE = True      # True for various debug messages, False for a more silent execution.
net_server = None
MAINTENANCE_PERIOD = 2.0

class Node_Info():
    """This is struct containing the info of other nodes.  
    We use this, rather than the node class itself, for entries in the finger table
    as well as successor and predecessor.   
    """
    def __init__(self, IPAddr, ctrlPort, key=None):
        if key is None:
            self.key = hash_str(IPAddr+":"+str(ctrlPort))
        else:
            self.key = key
        self.loc = spacemath.hash2loc(self.key)
        self.IPAddr = IPAddr
        self.ctrlPort = ctrlPort
        ##print self.IPAddr, self.ctrlPort, str(self.key)

    def __str__(self):
        return self.IPAddr+":"+str(self.ctrlPort)+">"+str(self.key)
    
    def __eq__(self,other):
        if other == None:
            return False
        return self.key == other.key
        
    def __ne__(self,other):
        if other == None:
            return True
        return not self.key == other.key

    def __str__(self):
        return str(self.IPAddr)+":"+str(self.ctrlPort)+":"+str(self.key)

    def  __hash__(self):
        return int(self.key.key,16)


"""This class represents the current node in the Chord Network.
We try to follow Stoica et al's scheme as closely as possible here,
except their methods aren't asynchronus.  Our changes are listed below

1.  Like Stoica et al, finger[1] is the successor. This keeps the math identical.
    However, lists index beginning at 0, so finger[0] is used to store the predecessor
2.  To call functions on other nodes, we pass them a message, like in the case of notify().
    We don't have the other node's node object available to us, so we send it a message
    which will make the node call notify()
"""

thisNode = None
IPAddr = "THIS IS WRONG"
ctrlPort = 9500
key = ""

peers = []
blacklist = []


#services
services = {}
services_lock = Lock()


#Network connections
servCtrl = None
servRelay = None

###########
# Find successor
###########

#  This is find successor and find closest predecessor rolled into one.
def find_ideal_forward(key):
    ##print key
    return spacemath.v_filter(spacemath.hash2loc(key), peers+[thisNode])



######
# Ring and Node Creation
######


# create a new Chord ring.
# TODO: finger table?
def create():
    global key, thisNode
    if TEST_MODE:
        print "Create"
    key = thisNode.key
    peers = []

# join node node's ring
# TODO: finger table?   CHeck to refactor
# this we need to modify for asynchronus stuff 
def join(node):
    global peers
    if TEST_MODE:
        print "Join"
    peers = [node]
    find = Find_Successor_Message(thisNode, thisNode.key, thisNode)
    send_message(find, node)

#########We shoudl clean this up    
def startup():
    if TEST_MODE:
        print "Startup"
    t = Thread(target=kickstart)
    t.setDaemon(True)
    t.start()
    for i in range(0,2):
        t = Thread(target=message_handler_worker)
        t.setDaemon(True)
        t.start()

def kickstart():
    if TEST_MODE:
        print "Kickstart"
    begin_stabilize()
    while True:
        time.sleep(MAINTENANCE_PERIOD)
        begin_stabilize()


##END CLEANUP


#############
# Maintenence
#############

# called periodically. n asks the successor
# about its predecessor, verifies if n's immediate
# successor is consistent, and tells the successor about n

def begin_stabilize():
    global peers
    if TEST_MODE:
        print "Begin Stabilize"
    peers = spacemath.peer_reduce(thisNode, peers)
    for p in peers:
        message = Stablize_Message(thisNode,p)###UPDATE
        temppeers = [thisNode]+peers
        temppeers.remove(p)
        message.add_content("peers",temppeers)
        send_message(message, p)
# need to account for successor being unreachable
def stabilize(message):
    global peers, blacklist
    if TEST_MODE:
        print "Stabilize"
    x = message.get_content("peers")
    newblacklist = []
    for p in blacklist:
        if p in x:
            x.remove(p)
            newblacklist.append(p)
    blacklist = newblacklist
    peers = spacemath.peer_reduce(thisNode, peers+x)

# TODO: Call this function
# we couldn't reach our successor;
# He's dead, Jim.
# goto next item in the finger table
# TODO: if pred is thisNode. 
def stabilize_failed(p): ###update call to this function
    if TEST_MODE:
        print "Stabilize Failed"
    if p in peers:
        peers.remove(p)
    blacklist.append(p)

###############################
# Service Code
###############################


def add_service(service):
    global services
    global thisNode
    services[service.attach(thisNode, send_message)] = service
    if VERBOSE: 
        print "Service " + service.service_id + "attached" 


def send_message(msg, destination):
    #TODO: write something to actually test this
    if destination == None:
        destination = find_ideal_forward(msg.destination_key)

    #remote_ip, remote_port, raw_data, success_callback_msg=None, failed_callback_msg=None):
    if destination == thisNode:
        handle_message(msg)
    else:
        net_server.send_message(msg, destination)

# called when node is passed a message

"""
Our problem is that there are three scenarios for handling the message, not 2
1) I'm responsible
2) I'm not responsible, but I know who is (ie, the successor)
3) I don't know, but I know who else to ask

Our problem, I think, is we were cludging together 1 and 2 and 2 and 3
"""

def I_own_hash(hkey):
    return thisNode == spacemath.v_filter(spacemath.hash2loc(hkey),[thisNode]+peers)

todo = Queue.PriorityQueue()

def message_handler_worker():
    while(True):
        priority, msg = todo.get(True)
        worker_handle_message(msg)
        todo.task_done()

def handle_message(msg):
    todo.put((msg.priority, msg))

def worker_handle_message(msg):
    if I_own_hash(msg.destination_key) :
        try:
            myservice = services[msg.service]
        except KeyError:
            print "msg dropped!\n service was:", msg, msg.service
            print "attached services are:"
            print services.keys()
            return
        myservice.handle_message(msg)
    else:
        print "forwarding a message"
        forward_message(msg)

def forward_message(message):
    if not I_own_hash(message.destination_key):
        closest = find_ideal_forward(message.destination_key)
        message.origin_node = thisNode
        send_message(message, closest)

def message_failed(msg, intended_dest):
    print msg, intended_dest
    stabilize_failed(intended_dest)
    send_message(msg,None)

