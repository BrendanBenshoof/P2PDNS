#!/usr/bin/env python
###Startup and commandline file
import service
import shelver as db 
import hash_util
import random
import simple_network
import voronoinode as node
import time
import Queue
import os
import filesystem_service
import threading 
import sys
import map_reduce
import minerServ
import httpservice
import json
from urllib2 import urlopen

local_mode=False
selfdestruct = False

print "starting and waiting"
#time.sleep(random.randint(10,60))
print "done waiting"


def myIP():
    if not local_mode:
        myip = json.load(urlopen('http://httpbin.org/ip'))['origin']
        print "just got my ip:", myip
        return myip
    else:
        return "127.0.0.1"
    

# backwards-compatibility use of global vars...encapsulation is easily
# possible by ensuring all functionality lives in a service with a reference
# to router which would then be instantiated in main()
services = {}
commands = {}

def add_service(service_object):
    s_name = service_object.service_id
    services[s_name] = service_object

def attach_services():
    for s_name in services.keys():
        node.add_service(services[s_name])
        commands_list = services[s_name].attach_to_console()
        if not commands_list is None:
            for c in commands_list:
                commands[c] = services[s_name]

def setup_Node(addr="localhost", port=None):
    node.IPAddr = addr
    node.ctrlPort = port
    node.thisNode = node.Node_Info(node.IPAddr, node.ctrlPort)
    #node.net_server = dummy_network.start(node.thisNode, node.handle_message)
    node.net_server = simple_network.NETWORK_SERVICE("", node.ctrlPort)
    #### setup services here
    database_name = str(node.thisNode.key)+".db"
    database = db.Shelver(database_name)
    add_service(database)
    add_service(service.Internal_Service())
    add_service(service.ECHO_service())
    add_service(filesystem_service.FileSystem())
    add_service(map_reduce.Map_Reduce_Service())
    minerserv = minerServ.Miner_Service()
    add_service(minerserv)
    add_service(httpservice.WEBSERVICE(database, minerserv.chainHandler))
    
    ####
    attach_services()


def join_ring(node_name, node_port):
    othernode = node.Node_Info(node_name, node_port)
    node.join(othernode)

def no_join():
    node.create()

def console():
    cmd = "-"
    loaded_script = Queue.Queue()
    try:
        if loaded_script.empty():
            cmd = raw_input()
        else:
            cmd = loaded_script.get()
            loaded_script.task_done()
    except EOFError: #the user does not have a terminal
        pass
    while not ( cmd == "q" or cmd == "Q"):
        command, args = None, None
        splitted = cmd.split(' ',1)
        if len(splitted) >= 1:
            command = splitted[0]
        if len(splitted) == 2:
            args = splitted[1]
        if command in commands.keys():
            mytarget = lambda: commands[command].handle_command(command, args)
            t = threading.Thread(target=mytarget)
            t.daemon = True
            t.start()
        elif command == "run":
            file2open = file(args,"r")
            for l in file2open:
                loaded_script.put(l)
            file2open.close()
        elif command == "stat":
            input_size = node.todo.qsize();
            print "backlog: "+str(input_size)
            if input_size > 0:
                print threading.activeCount(), "Active threads. Cheating, spawning new worker."
                t = threading.Thread(target=node.message_handler_worker)
                t.setDaemon(True)
                t.start()
        elif command == "threads":
            for t in threading.enumerate():
                print t
        elif command == "num_threads":
            print threading.activeCount()
        else:
            print "peers", map(str,node.peers)
        try:
            if loaded_script.empty():
                cmd = raw_input()
            else:
                cmd = loaded_script.get()
                loaded_script.task_done()
        except EOFError:  # the user does not have a terminal
            #print "I do not see a terminal!"
            time.sleep(1)
            pass
    node.net_server.stop()
    os.exit()


def main():
    myip = myIP()
    node.IPAddr = myip
    args = sys.argv
    if len(args) > 1 and args[1] != "?":
        local_port = int(args[1]) 
    else: 
        local_port = random.randint(9000, 9999)
    print myip+":"+str(local_port)
    other_IP = args[2] if len(args) > 2 else None
    other_port = int(args[3]) if len(args) > 3 else None

    setup_Node(addr=myip,port=local_port)
    if not other_IP is None and not other_port is None:
        join_ring(other_IP, other_port)
    else:
        no_join()
    node.startup()
    console()

if __name__ == "__main__":
    main()

