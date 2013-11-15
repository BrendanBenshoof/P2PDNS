from message import *
from hash_util import *
import node

IRM =  "IRM"
POLL_MIN = 10.0    #A FILE WILL AT MOST ONCE EVERY POLL_MIN SECONDS
POLL_MAX = 60.0     # POLL AT LEAST ONCE A MINUTE

class IRM_Service(Service):
    """ This is a complete and total replacement for the Internal_Service Class based on"""
    def __init__(self, db_service):
        super(Service, self).__init__()
        self.service_id = IRM
        self.db_service = db_service
        self.polls = {}

    def handle_message(self, message):
        pass
    
    
    def create_replica(self, message):
        pass
    
    def delete_replica(self, message):
        pass



class Request_Info(object):
    def __init__(self, key):
        self.init_rate = 1
        self.forward_rate = 1
        self.init_threshold = 5
        self.forward_threshold = 5

class Replica_Info(object):
    """information about a key we've made a replica for"""
    def __init__(self, key):
        self.key = key              # the key of the data we are keeping a local replica of
        self.next_poll =  MAX_POLL_RATE          # This is TTR 
        self.increase_rate = 1      # additive increase in seconds
        self.decrease_rate = 0.75    # multiplicative decrease ratio
                
    def adjust_polling(self, stale):
        if stale:
            self.next_poll = self.next_poll * self.decrease_rate
        else:
            self.next_poll = self.next_poll + self.increase_rate
        self.next_poll = max(POLL_MIN, min(POLL_MAX, self.next_poll))
    
    
