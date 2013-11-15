jobid = "sum"

##calculate pi mapreduce job
from map_reduce import Data_Atom
## assume contents is a line of text
import random
def map_func(atom):
    print "map sum",atom.contents
    jobid = atom.jobid
    total = 0L
    total+=atom.contents
    results = (total,0)
    atom = Data_Atom("", atom.hashkeyID, results)    
    atom.jobid = jobid
    return atom


def reduce_func(atom1, atom2):
    print "reduce sum",atom1.contents,atom2.contents
    if atom2.jobid == atom2.jobid:
        jobid = atom2.jobid
    else:
        raise Exception("unmatched jobs in reduce")
    result = atom1.contents[0]+atom2.contents[0]
    results = [result,0]
    atom = Data_Atom("", atom1.hashkeyID, results)
    atom.jobid = atom1.jobid
    return atom


def stage():
    samples = 10000000
    jobs = 10000
    atoms = []
    last = 0
    for i in range(0,jobs):
        atoms.append(Data_Atom("sum",None,samples/jobs))
    print "DONE STAGE"
    return atoms
