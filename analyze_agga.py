import sys, os, subprocess
import Queue
import time
import shutil

# This program first 
# copy agga files to sensitivity dir
# ssh to a host, install R
# modify R code to process the agga file
# run R

workdir = '/users/jhe/workdir/sensitivity-analysis/'

def copy_files(aggaslist):
    aggadir = '/users/jhe/workdir/metawalker/src/'
    for file in aggaslist:
        src = os.path.join( aggadir, file )
        dist = os.path.join(
                '/users/jhe/workdir/sensitivity-analysis/datafiles.fixedimage',
                file)
        if os.path.exists(dist):
            overwrite = raw_input(dist + ' exists. overwrite?[y|n]')
            if overwrite == 'n':
                print 'skipped.'
                continue
        shutil.copy2( src, dist )
        print src, '->', dist

def install_R(workerhost):
    cmd = ['ssh', workerhost,
            'sudo', 'apt-get', 'install', '-y',
            'r-base-core']
    print cmd
    ret = subprocess.call(cmd)
    if ret != 0:
        print 'error when install_R'
        exit(1)

def modify_SA_code(aggafile):
    rfile = '/users/jhe/workdir/sensitivity-analysis/sensitivity-analysis-by-anova.R.0618'
    f = open(rfile, 'r')
    lines = f.readlines()
    f.close()

    f = open(RSCRIPTPATH, 'w+')
    for line in lines:
        if 'REPLACEME' in line:
            line = line.replace('TARGET', aggafile)
            print line,
        f.write(line)
    f.flush()
    f.close()

def run_R(aggafile, workerhost):
    # modify SA code
    rfile = '/users/jhe/workdir/sensitivity-analysis/sensitivity-analysis-by-anova.R.0618'
    targetfile = aggafile + '.R'
    targetpath = os.path.join(workdir, targetfile)

    f = open(rfile, 'r')
    lines = f.readlines()
    f.close()

    f = open(targetpath, 'w+')
    for line in lines:
        if 'REPLACEME' in line:
            line = line.replace('TARGET', aggafile)
            print line,
        f.write(line)
    f.flush()
    f.close()
    
    # run R
    cmd = ['ssh', workerhost,
            'R', '-f',
            targetpath]
    print cmd
    proc = subprocess.Popen(cmd)

    return proc

def generate_node_names(prefix, suffix, nodestr):
    # get all node names
    numbers = nodestr.split(",")
    nlist = []
    for n in numbers:
        if '-' in n:
            a,b = n.split('-')
            a = int(a)
            b = int(b)
            for i in range(a, b+1):
                nlist.append(i)
        else:
            nlist.append(n)

    nlist = [str(x) for x in nlist]
    nlist = [ prefix + x + '.' + suffix for x in nlist ] 

    return nlist

def main():
    argv = sys.argv
    if len(argv) != 4:
        print 'Usage:', argv[0], 'agga-files nodestr clustersuffix'
        print 'Example: python', argv[0], 'agga.3.0.0.txt 0,1 noloop.plfs'
        exit(1)

    aggas         = argv[1]
    aggaslist     = aggas.split(',')
    nodestr       = argv[2]
    clustersuffix = argv[3]

    hostnames = generate_node_names('h', clustersuffix, nodestr)
    print hostnames

    copy_files(aggaslist)

    # a job queue model
    jobq = Queue.Queue()
    for job in aggaslist:
        jobq.put(job)
    
    machineproc = {}

    while not jobq.empty():
        jobfile = jobq.get()
        print "Doing ", jobfile
        time.sleep(2)

        assigned = False
        while assigned == False:
            # update machine info
            # find a machine for this job
            for machine in hostnames:
                time.sleep(2)
                print 'looking at', machine
                if (not machineproc.has_key(machine)) or \
                        machineproc[machine].poll() != None:
                    # idle machine, use it
                    if not machineproc.has_key(machine):
                        # this machine has not been used
                        # we need to install R first
                        print machine, 'needs to install R first'
                        time.sleep(2)
                        install_R(machine)
                    else:
                        print 'ready to run, do not need installing R'
                        time.sleep(2)
                    machineproc[machine] = run_R(jobfile, machine)
                    assigned = True
                    break
                    
            time.sleep(1)

    # wait untill all processes finish
    for machine,proc in machineproc.items():
        print 'Waiting for', machine
        proc.wait()
        
if __name__ == '__main__':
    main()

