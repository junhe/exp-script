import sys, os, subprocess
import time
import shutil

# This program first 
# copy agga files to sensitivity dir
# ssh to a host, install R
# modify R code to process the agga file
# run R

RSCRIPTPATH = '/users/jhe/workdir/sensitivity-analysis/.tmp.R'

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

def run_R(workerhost):
    cmd = ['ssh', workerhost,
            'R', '-f',
            RSCRIPTPATH]
    print cmd
    ret = subprocess.call(cmd)
    if ret != 0:
        print 'error when running R'
        exit(1)

def main():
    argv = sys.argv
    if len(argv) != 3:
        print 'Usage:', argv[0], 'agga-files workerhost'
        print 'Example: python', argv[0], 'agga.3.0.0.txt h0.noloop.plfs'
        exit(1)

    aggas = argv[1]
    aggaslist = aggas.split(',')
    workerhost = argv[2]
    
    copy_files(aggaslist)
    install_R(workerhost)

    for file in aggaslist:
        modify_SA_code(file)
        print 'going to analyze', file
        time.sleep(1)
        run_R(workerhost)


if __name__ == '__main__':
    main()

