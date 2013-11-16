def parse(request):
    request =  request.split() # request is a string
    if len(request) == 2 :
        return handleAX(request)
    elif len(request)>=6 :
        return handleQuery(request)
        


def handleAX():
    pass
    

#asks the server to lookup this url
#returns a string with all the relvent entries
# records are the following format, each line's elements are tab seperated
# DATA	qname		qclass	qtype	ttl	id  content	
def queryServer(url):
    records  = "DATA\t"+url+"\tIN\t"+"A\t" + "3600\t" +"-1\t" +"123.45.67.89\n"
    records += "DATA\t"+url+"\tIN\t"+"A\t" + "3600\t" +"-1\t" +"123.45.67.90\n"
    records += "DATA\t"+url+"\tIN\t"+"A\t" + "3600\t" +"-1\t" +"123.45.67.91\n"
    records += "DATA\tchronus."+url+"\tIN\t"+"A\t" + "3600\t" +"-1\t" +"123.45.67.92\n"
    records += "DATA\t"+url+"\tIN\t"+"TXT\t" + "3600\t" +"-1\t" +"Hi mom!\n"
    records += "DATA\t"+url+"\tIN\t"+"SOA\t" + "3600\t" +"-1\t" +"ahu.example.com ns1.example.com 2008080300 1800 3600 604800 3600\n"
    records += "DATA\t"+url+"\tIN\t"+"CNAME\t" + "3600\t" +"-1\t" +"chronus."+url+"\n"
    records += "DATA\t"+url+"\tIN\t"+"NS\t" + "3600\t" +"-1\t" +"ns1.chronus.edu"
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
        elements = record.split()
        rtype =elements[3]
        if qtype == rtype or qtype =="ANY":
            response += record
            response += "\n"
    response += "END"
    return response


q1 = "Q\t"+"www.trapezoids.org\t" +"IN\t" +"A\t"+"-1\t"+"127.0.0.1"

print parse(q1)
