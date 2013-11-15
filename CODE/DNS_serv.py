from service import Service
from message import Message

##TODO
#make a simple web server to respond with DNS records on request, so we can make a little script to interface with powerDNS


class DNSService(Service):
    """Handler of Chord behavoir and internal messages"""
    def __init__(self):
        super(Service, self).__init__()
        self.service_id = "DNS"
        self.priority = 1 #normal priority

    def handle_message(self, msg):
        if not msg.service == self.service_id:
            raise Exception("Mismatched service recipient for message.")
        return True

    def attach_to_console(self):
        ### return a list of command-strings
        return []

    def handle_command(self, comand_st, arg_str):
        ### one of your commands got typed in