from message import *
from hash_util import *
from Queue import Queue
import voronoinode as node
import os
import time
from globals import *


class Service(object):
    """This object is intented to act as a parent/promise for Service Objects"""
    def __init__(self):
        self.service_id = None
        self.callback = None
        self.owner = None
        self.priority = 10 #lowest


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
        return msg.service == self.service_id

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


class ECHO_service(Service):
    def __init__(self):
        super(Service, self).__init__()
        self.service_id = SERVICE_ECHO
        self.priority = 1 #almost highest

    def handle_message(self, msg):
        if not msg.service == self.service_id:
            raise Exception("Mismatched service recipient for message.")

        for k in msg.contents.keys():
            print k+":"+str(msg.get_content(k))



class Internal_Service(Service):
    """Handler of Chord behavoir and internal messages"""
    def __init__(self):
        super(Service, self).__init__()
        self.service_id = SERVICE_INTERNAL
        self.priority = 0 #highest priority
    def handle_message(self, msg):
        if not msg.service == self.service_id:
            raise Exception("Mismatched service recipient for message.")


        """This function is called whenever the node recives a message bound for this service"""
        """Return True if message is handled correctly
        Return False if things go horribly wrong
        """
        ## switch based on "type"
        msgtype = msg.type
        response = None
        if node.TEST_MODE:
            print "Got " + str(msgtype) +  " from " + str(msg.origin_node)
        if msgtype == FIND:  # This might not ever happen with new changes
            response = Update_Message(self.owner, msg.reply_to.key, msg.finger)
        elif msgtype == STABILIZE:
            node.stabilize(msg)
 
        else:
            return False
        if response != None:
            self.callback(response, msg.reply_to)
        return True

    def attach_to_console(self):
        ### return a list of command-strings
        return ["fingers","connect","quit"]

    def handle_command(self, comand_st, arg_str):
        ### one of your commands got typed in
        if comand_st == "fingers":
            count = 0
            fingers = {}
            for f in node.fingerTable:
                if not f is None:
                    count+=1
                    try:
                        fingers[f]+=1
                    except KeyError:
                        fingers[f]=1
            print "there are: "+str(count)+" finger entries"
            for f in fingers.keys():
                print f,":",fingers[f]
        elif comand_st == "quit":
            node.my_polite_exit()
        elif comand_st == "connect":
            args = arg_str.split(":")
            print args
            nodeip = args[0]
            nodePort = int(args[1])
            newnode = node.Node_Info(nodeip, nodePort)
            message = Stablize_Message(self.owner,newnode)###UPDATE
            message.add_content("peers",[self.owner]+node.peers)
            self.send_message(message, newnode)
