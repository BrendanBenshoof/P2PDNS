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


# Debug variables
TEST_MODE = False   #duh
VERBOSE = False      # True for various debug messages, False for a more silent execution.
net_server = None
MAINTENANCE_PERIOD = 0.2

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

predecessor= None
predecessor_lock = Lock()

successor = None
successor_lock = Lock()

#Finger table
fingerTable = None
fingerTable_lock = Lock()
#numFingerErrors = 0
next_finger = 100

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
    if successor != None and hash_between_right_inclusive(key, thisNode.key, successor.key):
        return successor
    return closest_preceding_node(key)



def closest_preceding_node(key):
    for finger in reversed(fingerTable[1:]): # or should it be range(KEY_SIZE - 1, -1, -1))
        if finger != None: 
            if hash_between(finger.key, thisNode.key, key): #Stoica's paper indexes at 1, not 0
                return finger   #this could be the source of our problem;  how do we distinguish between him being repsonsible and him preceding
    return thisNode


######
# Ring and Node Creation
######


# create a new Chord ring.
# TODO: finger table?
def create():
    global successor, predecessor, fingerTable, key, thisNode
    if TEST_MODE:
        print "Create"
    key = thisNode.key
    predecessor = thisNode
    successor = thisNode
    fingerTable = [thisNode, thisNode]  
    for i in range(2,KEY_SIZE+1):
        fingerTable.append(None)


# join node node's ring
# TODO: finger table?   CHeck to refactor
# this we need to modify for asynchronus stuff 
def join(node):
    global predecessor
    global fingerTable
    global successor
    if TEST_MODE:
        print "Join"
    predecessor = thisNode
    successor = thisNode
    fingerTable = [thisNode, thisNode]  
    for i in range(2,KEY_SIZE+1):
        fingerTable.append(None)
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
        time.sleep(MAINTENANCE_PERIOD)
        begin_stabilize()
        check_predecessor()        
        time.sleep(MAINTENANCE_PERIOD)
        fix_fingers(1)

##END CLEANUP


#############
# Maintenence
#############

# called periodically. n asks the successor
# about its predecessor, verifies if n's immediate
# successor is consistent, and tells the successor about n

def begin_stabilize():
    if TEST_MODE:
        print "Begin Stabilize"
    successor_lock.acquire(True) 
    message = Stablize_Message(thisNode,successor)
    successor_lock.release()
    send_message(message, successor)
    
# need to account for successor being unreachable
def stabilize(message):
    if TEST_MODE:
        print "Stabilize"
    x = message.get_content("predecessor")
    if x!=None and hash_between(x.key, thisNode.key, successor.key):
        update_finger(x,1)
    send_message(Notify_Message(thisNode, successor.key), successor)  #Andrew added second field on 8-11, checking to see if this resolves our issue. 
    

# TODO: Call this function
# we couldn't reach our successor;
# He's dead, Jim.
# goto next item in the finger table
# TODO: if pred is thisNode. 
def stabilize_failed():
    if TEST_MODE:
        print "Stabilize Failed"
    for entry in fingerTable[2:]:
        if entry != None:
            update_finger(entry,1)
            begin_stabilize()
            return

            
    #what to do here???

# we were notified by node other;
# other thinks it might be our predecessor
# TODO: if pred is thisNode.
def get_notified(message):
    global predecessor
    global fingerTable
    if TEST_MODE:
        print "Get Notified"
    other =  message.origin_node
    if(predecessor == thisNode or hash_between(other.key, predecessor.key, thisNode.key)):
        fingerTable_lock.acquire(True)
        predecessor_lock.acquire(True)
        predecessor = other
        fingerTable[0] = predecessor
        fingerTable_lock.release()
        predecessor_lock.release()
        if message.origin_node != thisNode:
            for s in services.values():
                s.change_in_responsibility(predecessor.key, thisNode.key)


def fix_fingers(n=1):
    global next_finger
    for i in range(0,n):
        if successor != thisNode and predecessor != thisNode:
            next_finger = next_finger + 1
            if next_finger > KEY_SIZE:
                next_finger = 1
            if TEST_MODE:
                print "Fix Fingers + " + str(next_finger)
            target_key = add_keys(thisNode.key, generate_key_with_index(next_finger-1))
            message = Find_Successor_Message(thisNode, target_key, thisNode, next_finger)
            send_message(message, None)

def update_finger(newNode,finger):
    global fingerTable
    global successor
    global predecessor
    #print "finger changed to", newNode, finger
    fingerTable_lock.acquire(True)
    if TEST_MODE:
        print "Update finger: " + str(finger)
    fingerTable[finger] = newNode
    fingerTable_lock.release()
    if finger == 1:
        if newNode is None:
            newNode = thisNode
        successor_lock.acquire(True)
        successor = newNode
        successor_lock.release()
    elif finger == 0:
        if newNode is None:
            newNode = thisNode
        predecessor_lock.acquire(True)
        predecessor = newNode
        predecessor_lock.release()

# ping our predecessor.  pred = nil if no response
def check_predecessor():
    if(predecessor != None or not hash_equal(predecessor.key, thisNode.key)):  # do this here or before it's called
        send_message(Check_Predecessor_Message(thisNode, predecessor.key),predecessor)
   
#politely leave the network 
def exit_network():
    pass


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
    return hash_between_right_inclusive(hkey, predecessor.key, thisNode.key)

todo = Queue.PriorityQueue()

def message_handler_worker():
    while(True):
        priority, msg = todo.get(True)
        worker_handle_message(msg)
        todo.task_done()

def handle_message(msg):
    todo.put((msg.priority, msg))

def worker_handle_message(msg):
    if I_own_hash(msg.destination_key) or successor == thisNode:  # if I'm responsible for this key
        if successor == thisNode and not successor == predecessor:
            print "!"
        try:
            myservice = services[msg.service]
        except KeyError:
            print "msg dropped!\n service was:", msg, msg.service
            print "attached services are:"
            print services.keys()
            return
        myservice.handle_message(msg)
    else:
        forward_message(msg)

def forward_message(message):
    if hash_between_right_inclusive(message.destination_key, thisNode.key, successor.key):
        message.origin_node = thisNode
        if TEST_MODE:
            print "not mine; forwarding to " + str(successor)
        send_message(message, successor)
    else:
        closest =  closest_preceding_node(message.destination_key)
        if TEST_MODE:
            print "not mine; forwarding to " + str(closest)
        if closest==thisNode:
            if TEST_MODE:
                print "I'm the closest, how did that happen"
        else:
            message.origin_node = thisNode
            send_message(message, closest)

def estimate_ring_density():
    total = 0
    i = 80
    count = 0
    for f in fingerTable[80:]:
        if not f is None:
            ideal = int(generate_key_with_index(i).key, 16)
            actual = int(f.key.key, 16)
            distance = actual-ideal
            total += distance*2
            i+=1
            count +=1
    average = total/count
    ring_size = 0x01 << 160
    return ring_size / average
    

def message_failed(msg, intended_dest):
    print msg, intended_dest
    print successor, predecessor
    for i in reversed(range(0,161)):
        if not fingerTable[i] is None:
            if fingerTable[i] == intended_dest:
                update_finger(None,i)
    send_message(msg,None)

def peer_polite_exit(leaveing_node):
    print "peer leaving"
    for i in range(0,160)[::-1]:
        if fingerTable[i] == leaveing_node:
            if i == 1: #we lost our successor
               update_finger(find_ideal_forward(thisNode.key),1)

            if i == 0: #we lost our predecessor
                update_finger(None,0)

            else: #we just lost a finger
                update_finger(None,i)

def my_polite_exit():
    done = []
    for p in fingerTable:
        if not p is None:
            quitMSG = Exit_Message(thisNode, p.key)
            send_message(quitMSG,p)
            done.append(p)
