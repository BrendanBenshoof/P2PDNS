from service import *
from message import *
import node
import hash_util
from math import pi
import time


class Toplogy_Poll_Message(Message):
    def __init__(self, origin_node, destination_key):
        Message.__init__(self,"TOPOLOGY","TOPOLOGY")
        self.origin_node = origin_node
        self.destination_key = destination_key
        self.service = SERVICE_TOPOLOGY
        self.type =  SERVICE_TOPOLOGY
        self.add_content("server_list",[str(origin_node)])
        self.add_content("link_list",{})
        self.add_content("start",origin_node.key)
        self.add_content("end",destination_key)
        self.reply_to = origin_node
        self.start_time = time.time()


class Topology(Service):
    def __init__(self):
        super(Topology, self).__init__()
        self.service_id = SERVICE_TOPOLOGY
        self.topology_guess = []
        self.last_start_time = 0.0

    def get_my_links(self):
        output = []
        for n in node.fingerTable:
            if not str(n) in output:
                output.append(str(n))
        return output

    def start_inquery(self):
        sucessor_cheat = hash_util.generate_lookup_key_with_index(self.owner.key,0)
        new_query = Toplogy_Poll_Message(self.owner,sucessor_cheat)
        #linkset = {str(node.thisNode): self.get_my_links()}
        new_query.add_content("N",1)
        self.send_message(new_query, None)
        print "Send Inquery"
        self.last_start_time = time.time()

    def attach_to_console(self):
        ### return a dict of command-strings
        return ["plot"]

    def handle_command(self, comand_st, arg_str):
        ### one of your commands got typed in
        self.start_inquery()


    def handle_message(self, msg):
            print "get inquery"
            """This function is called whenever the node recives a message bound for this service"""
            """Return True if message is handled correctly
            Return False if things go horribly wrong
            """
            if msg.service != self.service_id:
                return False
            start = msg.get_content("start")
            end = msg.get_content("end")
            N = msg.get_content("N")
            #record = msg.get_content("server_list")
            #linkset = msg.get_content("link_list")
            if not msg.reply_to == self.owner:
                if  not hash_util.hash_between(self.owner.key,start,end):
                    sucessor_cheat = hash_util.generate_lookup_key_with_index(self.owner.key,0)
                    msg.origin_node = self.owner
                    msg.destination_key = sucessor_cheat
                    #record.append(str(self.owner))
                    #linkset[str(node.thisNode)] = self.get_my_links()
                    #msg.add_content("server_list", record)
                    #msg.add_content("link_list",linkset)
                    msg.add_content("N",N+1)
                    self.send_message(msg, None)
                else:
                    msg.destination_key = msg.reply_to.key
                    self.send_message(msg, msg.reply_to)
            else:
                now = time.time()
                print "render inquery:", now - msg.start_time
                print N
                #print len(record)

def render(record, edges):
    import matplotlib.pyplot as plt
    import math
    record_matrix = map(lambda x: x.split(":"), record)
    myMax = int(2**160)
    x_points = [0.0]
    y_points = [0.0]
    names = ["origin"]
    print record_matrix
    for r in record_matrix:
        name = str(r[0])+":"+str(r[1])
        int_id = int(r[2][2:],16)
        ratio = int_id*1.0/myMax
        theta = math.pi*2.0*ratio
        x = math.sin(theta)
        y = math.cos(theta)
        print x, y, name
        x_points.append(x)
        y_points.append(y)
        plt.annotate(name, xy = (x, y))
    plt.plot(x_points,y_points,"o")
    plt.show()
