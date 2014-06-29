import sys
import time
import os
import subprocess

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = newPath

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

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
    nlist = [ prefix + x + suffix for x in nlist ] 

    return nlist

def download(version, clustersuffix, node):
    "node exmple: h0, only one node is supported"
    tar_version = get_tar_version(version)
    tarball = 'linux-'+tar_version+'.tar.gz'
    print "downloading...", tarball
    with cd("/users/jhe/Home2/tars"):
        # download
        ver_items = version.split('.')
        ver_dir = ""
        if ver_items[0] == '3':
            ver_dir = 'v3.x/'
        elif ver_items[0] == '2' and ver_items[1] == '6':
            ver_dir = 'v2.6/'
        else:
            print version, 'is not supported'

        suffolder = ""
        if 'rc' in version:
            suffolder = 'testing/'

        ret = subprocess.call(
            ['wget',
             '-N',
             'https://www.kernel.org/pub/linux/kernel/'+
              ver_dir + suffolder 
              + tarball,
             '--no-check-certificate'])
        if ret != 0:
            print 'error at wget'
            exit(1)
        # scp
        ret = subprocess.call(
            ['scp', 
             '/users/jhe/Home2/tars/'+tarball,
             node+'.'+clustersuffix+':/mnt/scratch-sda4/'])
        if ret != 0:
            print 'error at scp'
            exit(1)
        # untar at the node
        cmd = ['ssh', node+'.'+clustersuffix,
             'bash', '-c', 
             '"cd /mnt/scratch-sda4/ && pwd && tar -xf '
               +tarball+'"']
        print cmd
        ret = subprocess.call(cmd)
        if ret != 0:
            print 'error at tar'
            exit(1)


def make_oldconfig(version, clustersuffix, node):
    tar_version = get_tar_version(version)
    cmd = ['ssh', node+'.'+clustersuffix,
           'bash', '-c',
           '"cd /mnt/scratch-sda4/linux-'+tar_version+
           ' rm -f .config* && cp -v ~/Home2/tars/.config-3.0-jun.loop.nfs .config && ' +
           ' yes \'\' |make oldconfig "']
    print cmd
    ret = subprocess.call(cmd)
    if ret != 0:
        print 'error at make oldconfig'
        exit(1)

def make_kernel(version, clustersuffix, node):
    tar_version = get_tar_version(version)
    cmd = ['ssh', node+'.'+clustersuffix,
           'bash', '-c',
           '"cd /mnt/scratch-sda4/linux-'+tar_version+
           '&& make -j3"']
    print cmd
    print 'hello'
    ret = subprocess.call(cmd)
    if ret != 0:
        print 'error at make_kernel'
        exit(1)

def wait_for_alive(nodelist, clustersuffix):
    nodelist = generate_node_names('h',
                        '.'+clustersuffix,
                        nodelist)
    while True:
        goodcnt = 0
        print '***** wait for nodes to back on ******'
        for node in nodelist:
            cmd = ['ssh',
                    '-o', 'ConnectTimeout=1',
                    '-o', 'BatchMode=yes',
                    node, 'exit']
            print cmd
            ret = subprocess.call(cmd)
            print node, 'returned', ret
            if ret == 0:
                goodcnt += 1
        if goodcnt == len(nodelist):
            break
        time.sleep(1)

def check_current_version(nodelist, clustersuffix):
    cmd = ['python', '/users/jhe/bin/runall.ssh.py',
            nodelist, '.'+clustersuffix,
            'uname -r', 'sync']
    print cmd
    ret = subprocess.call(cmd)
    if ret != 0:
        print 'error at check_current_version'
        exit(1)

def clean(nodelist, clustersuffix):
    cmd = ['python', '/users/jhe/bin/runall.ssh.py',
            nodelist, '.'+clustersuffix,
            'sudo pkill python', 'sync']
    print cmd
    ret = subprocess.call(cmd)
    if ret != 0:
        print 'error at clean'
        exit(1)

def get_node_list(nodestr):
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
    nlist = [int(x) for x in nlist]
    return nlist


def get_releasename(version):
    return version+'jun'

def get_tar_version(version):
    if '-' in version:
        nums,suf = version.split('-')
    else:
        nums = version
        suf = ""
    version_nums = nums.split('.')
    if version_nums[-1] == '0':
        # delete tailing 0
        del version_nums[-1]
        tar_version = '.'.join( version_nums )
        if suf != "":
            tar_version = '-'.join( [tar_version, suf] )
    else:
        tar_version = version
    return tar_version

def main():
    argv = sys.argv
    if len(argv) != 5:
        print "Usage:", argv[0], \
             'version nodelist clustersuffix usefinished|notusefinished funclist'
        print 'example:', argv[0], \
             "3.0.0 0 noloop.plfs " \
             "download,make_oldconfig," \
             "make_kernel"
        print "note that it only supports one node"
        exit(1)
    version    =argv[1]
    node       =argv[2]
    clustersuffix =argv[3]
    funclist = argv[4].split(',')


    if 'download' in funclist:
        download(version, clustersuffix, node)
    if 'make_oldconfig' in funclist:
        make_oldconfig(version, clustersuffix, node)
    if 'make_kernel' in funclist:
        make_kernel(version, clustersuffix, node)

if __name__ == '__main__':
    main()
    #print get_tar_version(sys.argv[1])
