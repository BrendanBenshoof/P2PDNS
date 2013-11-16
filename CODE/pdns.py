#!/usr/bin/python
import sys
import urllib2

sin = sys.stdin
out = sys.stdout
log = open("/home/andrew/P2PDNS/CODE/log",'w')

def parse(request):
    log.write(request)
    log.flush()
    request =  request.split() # request is a string    
    if len(request) == 2 :
        return handleAX(request)
    elif len(request)>=6 :
        return handleQuery(request)
        


def handleAX(q):
    return "END\n"

#asks the server to lookup this url
#returns a string with all the relvent entries
# records are the following format, each line's elements are tab seperated
# DATA	qname		qclass	qtype	ttl	id  content	
def queryServer(url):
    records = urllib2.urlopen("http://127.0.0.1:9080/"+url).read()
    """if url.startswith("cname."):
        return "DATA\tcname."+url+"\tIN\t"+"A\t" + "3600\t" +"-1\t" +"123.45.67.91"
    records  = "DATA\t"+url+"\tIN\t"+"A\t" + "3600\t" +"-1\t" +"123.45.67.89\n"
    records += "DATA\t"+url+"\tIN\t"+"A\t" + "3600\t" +"-1\t" +"123.45.67.90\n"
    records += "DATA\tcname."+url+"\tIN\t"+"A\t" + "3600\t" +"-1\t" +"123.45.67.91\n"
    records += "DATA\t"+url+"\tIN\t"+"A\t" + "3600\t" +"-1\t" +"123.45.67.92\n"
    records += "DATA\t"+url+"\tIN\t"+"TXT\t" + "3600\t" +"-1\t" +"Hi mom!\n"
    records += "DATA\t"+url+"\tIN\t"+"SOA\t" + "3600\t" +"-1\t" +"ahu.example.com\n"
    records += "DATA\t"+url+"\tIN\t"+"CNAME\t" + "3600\t" +"-1\t" +"cname."+url+"\n"
    records += "DATA\t"+url+"\tIN\t"+"NS\t" + "3600\t" +"-1\t" +"ns1.chronus.edu"
    """
    if recods.startswith("40"):
        return "FAIL"
    return records


def handleQuery(query):
    Q = query[0]        # "Q"
    qname = query[1]    # target to lookuo
    qclass = query[2]   # should be IN
    qtype = query[3]    # desired record type
    qid =  query[4]     
    asker= query[5]
    
    records = queryServer(qname)
    if records =="FAIL":
        return records
        
    records = records.split("\n")
    response = "" 
    for record in records:
        if record == [] or record.startswith("#"):
            continue
        elements = record.split()
        rtype =elements[3]
        if qtype == rtype or qtype =="ANY":
            response += record
            response += "\n"
    response += "END\n"
    return response



def read(sin, out):
    helo = sin.readline()
    log.write(helo)
    log.flush()
    if not helo.startswith("HELO"):
        return
    out.write("OK\n")
    log.write("OK\n")
    out.flush()
    log.flush()
    while True:
        line = sin.readline()
        if not line:
            break
        ans = parse(line)
        log.write(ans)
        out.write(ans)
        out.flush()
        log.flush()
#q1 = "Q\t"+"www.trapezoids.org\t" +"IN\t" +"A\t"+"-1\t"+"127.0.0.1"

read(sin, out)
