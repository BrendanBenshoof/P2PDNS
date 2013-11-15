jobid = "pi"



##calculate pi mapreduce job
from map_reduce import Data_Atom
## assume contents is a line of text
import random
def map_func(atom):
    print "map pi"
    jobid = atom.jobid
    resultin = 0L
    total = 0L
    print "running a map"
    points = atom.contents
    random.seed(int(atom.hashkeyID.key,16))
    for p in range(0,points):
        x = random.random()
        y = random.random()
        if (x**2.0)+(y**2.0) <= 1.0:
            resultin+=1
        total+=1
    results = (resultin, total)
    atom = Data_Atom("", atom.hashkeyID, results)    
    atom.jobid = jobid
    return atom


def reduce_func(atom1, atom2):
    if atom2.jobid == atom2.jobid:
        jobid = atom2.jobid
    else:
        raise Exception("unmatched jobs in reduce")
    "the form of this is probably wrong"
    a1 = atom1.contents[0]
    a2 = atom2.contents[0]
    b1 = atom1.contents[1]
    b2 = atom2.contents[1]
    results = (a1+a2, b1+b2)
    atom = Data_Atom("", atom1.hashkeyID, results)
    atom.jobid = atom1.jobid
    return atom


def stage():
    samples = 10000 #midsize run
    jobs = 500
    atoms = []
    last = 0
    for i in range(0,jobs):
        atoms.append(Data_Atom("pi",None,samples/jobs))
    print "DONE STAGE"
    return atoms
