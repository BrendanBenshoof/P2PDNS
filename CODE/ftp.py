import service
import message
import voronoinode as node
import hash_util
import shelver
import base64
##chord ftp service

class FTP_Service(Service):
    def __init__(self):
        super(FTP_Service, self).__init__()
        self.service_id = "FTP"
        self.root_dir = None
        self.local_dir = "/"
        self.outstanding_jobs=[]
        self.partial_files = {}

    def attach_to_console(self):
        ### return a dict of command-strings
        return ["cd","ls","mkdir","rm","put","get","lcd","lls","pwd","lpwd"]

    def handle_command(self, comand_st, arg_str):
        ### one of your commands got typed in
        pass

    def handle_message(self, msg):
        pass

    def parse_command(self, cmd,argslist):
        if cmd == "cd"
    
    def fail(errormsg):
        print errormsg

    def getfileinfo(self,path,task):
        fileloc = hash_util.hash_str(path)
        request_message = shelver.Database_Message(self.owner, fileloc, Response_service="FTP", file_type="GET")
        self.send_message(request_message,None)
        self.outstanding_jobs.append(("get",fileloc,task))

    def start_rebuilt_file(self,fileinfo,task):
        data = fileinfo.split("\n")
        filename = data[0]
        chunkIDs = data[1:]
        for c in chunkIDs:
            chunkloc = hash_util.Key(c)
            request_message = shelver.Database_Message(self.owner, chunkloc, Response_service="FTP", file_type="GET")
            self.send_message(request_message,None)
            self.outstanding_jobs.append(("assemble",chunkloc,lambda x: self.rebuild_file_from_parts(filename,x) ))
        size = len(chunkIDs)*2
        self.partial_files[filename] = map(lambda x: None, range(0,size))

    def rebuild_file_from_parts(self, fileid, part):
        data = part.split("\n")
        chunk_id = data[0]
        cid = int(chunk_id)
        for i in range(0,4):
            self.partial_files[fileid][cid+i] = data[i+1]

def chunkify_file(filename):
    openfile = file(filename,"r")

        
