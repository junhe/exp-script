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

def distribute_images(nodelist, clustersuffix):
    # copy to h0 first
    cmd = ['ssh', 'h0.'+clustersuffix,
           'bash', '-c',
           '"rsync -a --ignore-existing ' +
           '/users/jhe/Home2/tars/imgs-3.0.0/* /mnt/scratch-sda4/"']
    print cmd
    ret = subprocess.call(cmd)
    if ret != 0:
        print 'error at scp tar.gz'
        exit(1)

    # everybody else pull the images
    nlist = get_node_list(nodelist)
    nlist[:] = [ str(x) for x in nlist if x != 0 ]
    nlist = ','.join(nlist)

    cmd = ['python', '/users/jhe/bin/runall.ssh.py',
            nlist, '.'+clustersuffix,
            'rsync -a --ignore-existing h0.'+clustersuffix+':/mnt/scratch-sda4/h*marmot*.tar.gz '+
            '/mnt/scratch-sda4/',
            'sync']
    print cmd
    ret = subprocess.call(cmd)
    if ret != 0:
        print 'error at pull images'
        exit(1)   

    # untar
    cmd = ['python', '/users/jhe/bin/runall.ssh.py',
            nodelist, '.'+clustersuffix,
            'cd /mnt/scratch-sda4/ && ' +
            'ls h*marmot*.tar.gz | xargs -I% tar xvf %',
            'async']
    print cmd
    ret = subprocess.call(cmd)
    if ret != 0:
        print 'error at untar image'
        exit(1)   



def download(version, clustersuffix):
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
             'h0.'+clustersuffix+':/mnt/scratch-sda4/'])
        if ret != 0:
            print 'error at scp'
            exit(1)
        # untar at h0
        cmd = ['ssh', 'h0.'+clustersuffix,
             'bash', '-c', 
             '"cd /mnt/scratch-sda4/ && pwd && tar -xf '
               +tarball+'"']
        print cmd
        ret = subprocess.call(cmd)
        if ret != 0:
            print 'error at tar'
            exit(1)


def patch(patches, version, clustersuffix):
    tar_version = get_tar_version(version)
    srcdir = 'linux-'+tar_version

    if patches.lower() == 'nopatches':
        return

    patches = patches.split(',')
    # copy to h0
    for patch in patches:
        cmd = ['scp', '/users/jhe/Home2/patches/'+patch,
                'h0.'+clustersuffix+':/mnt/scratch-sda4/']
        ret = subprocess.call(cmd)
        if ret != 0:
            print 'failed to copy patch'
            exit(1)

    # apply the patches
    for patch in patches:
        cmd = ['ssh', 'h0.'+clustersuffix,
               'bash', '-c',
               '"cd /mnt/scratch-sda4/'+srcdir
               + ' && patch -p1 < ../' + patch +'"']
        ret = subprocess.call(cmd)
        if ret != 0:
            print 'failed to apply patch'
            exit(1)


def make_oldconfig(version, clustersuffix):
    tar_version = get_tar_version(version)
    cmd = ['ssh', 'h0.'+clustersuffix,
           'bash', '-c',
           '"cd /mnt/scratch-sda4/linux-'+tar_version+
           ' rm -f .config* && cp -v ~/Home2/tars/.config-3.0-jun.loop.nfs .config && ' +
           ' yes \'\' |make oldconfig "']
    print cmd
    ret = subprocess.call(cmd)
    if ret != 0:
        print 'error at make oldconfig'
        exit(1)

def make_kernel(version, clustersuffix):
    tar_version = get_tar_version(version)
    cmd = ['ssh', 'h0.'+clustersuffix,
           'bash', '-c',
           '"cd /mnt/scratch-sda4/linux-'+tar_version+
           '&& make -j3"']
    print cmd
    print 'hello'
    ret = subprocess.call(cmd)
    if ret != 0:
        print 'error at make_kernel'
        exit(1)


def tar_src(version, clustersuffix):
    tar_version = get_tar_version(version)
    releasename = get_releasename(version)
    cmd = ['ssh', 'h0.'+clustersuffix,
           'bash', '-c',
           '"cd /mnt/scratch-sda4/ && '
           'tar -cf linux-'+releasename+'.tar.gz linux-'+tar_version+'"']
    print cmd
    ret = subprocess.call(cmd)
    if ret != 0:
        print 'error at tar_src'
        exit(1)

def pull_src_tar(version, nodelist, clustersuffix):
    tar_version = get_tar_version(version)
    releasename = get_releasename(version)
    nlist = get_node_list(nodelist)
    nlist[:] = [ str(x) for x in nlist if x != 0 ]
    nlist = ','.join(nlist)

    cmd = ['python', '/users/jhe/bin/runall.ssh.py',
            nlist, '.'+clustersuffix,
            "scp h0."+clustersuffix+
                ":/mnt/scratch-sda4/linux-"+
                releasename+
                ".tar.gz /mnt/scratch-sda4/linux-"+
                releasename+".tar.gz",
            'sync']
    print cmd
    ret = subprocess.call(cmd)
    if ret != 0:
        print 'error at pull_src_tar'
        exit(1)
           
def untar_src(version, nodelist, clustersuffix):    
    tar_version = get_tar_version(version)
    releasename = get_releasename(version)
    nlist = get_node_list(nodelist)
    nlist[:] = [ str(x) for x in nlist if x != 0 ]
    nlist = ','.join(nlist)

    cmd = ['python', '/users/jhe/bin/runall.ssh.py',
            nlist, '.'+clustersuffix,
            "cd /mnt/scratch-sda4/ && " +
              "tar xf linux-"+releasename+".tar.gz",
            'async']
    print cmd
    ret = subprocess.call(cmd)
    if ret != 0:
        print 'error at untar_src'
        exit(1)

def install_kernel(version, nodelist, clustersuffix):
    tar_version = get_tar_version(version)
    releasename = get_releasename(version)
    srcdir = '/mnt/scratch-sda4/linux-'+tar_version

    cmd = ['python', '/users/jhe/bin/runall.ssh.py',
            nodelist, '.'+clustersuffix,
            'cd '+srcdir+' && '+
            'sudo make modules_install && '+
            'sudo make install',
            'async']
    print cmd
    ret = subprocess.call(cmd)
    if ret != 0:
        print 'error at install_kernel'
        exit(1)
            
def set_default_kernel(version, nodelist, clustersuffix):
    tar_version = get_tar_version(version)
    releasename = get_releasename(version)

    cmd = ['python', '/users/jhe/bin/runall.ssh.py',
            nodelist, '.'+clustersuffix,
            "sudo python /users/jhe/bin/set-default-kernel.py "+
                releasename,
            'async']
    print cmd
    ret = subprocess.call(cmd)
    if ret != 0:
        print 'error at set_default_kernel'
        exit(1)


def reboot(nodelist, clustersuffix):
    cmd = ['python', '/users/jhe/bin/runall.ssh.py',
            nodelist, '.'+clustersuffix,
            'sudo reboot', 'async']
    print cmd
    ret = subprocess.call(cmd)
    if ret != 0:
        print 'error at reboot'
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

def never_writeback(nodelist, clustersuffix):
    file1 = '/proc/sys/vm/dirty_writeback_centisecs'
    file2 = '/proc/sys/vm/dirty_expire_centisecs'
    cmd = ['python', '/users/jhe/bin/runall.ssh.py',
            nodelist, '.'+clustersuffix,
            'echo 9999999 | sudo tee '+file1, 'async']
    print cmd
    ret = subprocess.call(cmd)
    if ret != 0:
        print 'error at writing file1'
        exit(1)

    cmd = ['python', '/users/jhe/bin/runall.ssh.py',
            nodelist, '.'+clustersuffix,
            'echo 9999999 | sudo tee '+file2, 'async']
    print cmd
    ret = subprocess.call(cmd)
    if ret != 0:
        print 'error at writing file2'
        exit(1)

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

def run_exp(version, jobtag, nodelist, clustersuffix, arg_usefinished):
    cmd = ['ssh', 'h0.'+clustersuffix,
           'bash', '-c',
           '"cd /users/jhe/workdir/metawalker/src && ' +
           'python start_jobmaster.py agga.fixedimg-'+version+'.txt ' +
           jobtag + " " + arg_usefinished + '"']
    print cmd
    proc = subprocess.Popen(cmd)

    time.sleep(5)
    nlist = get_node_list(nodelist)
    np = str(len(nlist))
    cmd_workder = ['ssh', 'h0.'+clustersuffix,
           'bash', '-c',
           '"cd /users/jhe/workdir/metawalker/src && ' +
           'python start_worker.py' + 
                ' h0.'+clustersuffix+' '+clustersuffix+
                ' '+np+'"']
    print cmd_workder
    ret = subprocess.call(cmd_workder)
    if ret != 0:
        print 'error at worker'
        exit(1)
    time.sleep(3)
    print 'workers have been terminated!'
    sys.stdout.flush()

    proc.wait()


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
    if len(argv) != 8:
        print "Usage:", argv[0], \
             'version patches jobtag nodelist clustersuffix usefinished|notusefinished funclist'
        print 'example:', argv[0], \
             "3.0.0 patch1.patch,patch2.patch tag01 0-7 noloop.plfs notusefinished " \
             "distribute_images,download,patch,make_oldconfig," \
             "make_kernel,tar_src,pull_src_tar,untar_src,install_kernel," \
             "set_default_kernel,reboot,wait_for_alive,never_writeback,check_current_version," \
             "clean,run_exp"
        exit(1)
    version    =argv[1]
    patches    =argv[2]
    jobtag = argv[3]
    nodelist   =argv[4]
    clustersuffix =argv[5]
    arg_usefinished = argv[6]
    funclist = argv[7].split(',')

    if 'distribute_images' in funclist:
        distribute_images(nodelist, clustersuffix)
    if 'download' in funclist:
        download(version, clustersuffix)
    if 'patch' in funclist:
        patch(patches, version, clustersuffix)
    if 'make_oldconfig' in funclist:
        make_oldconfig(version, clustersuffix)
    if 'make_kernel' in funclist:
        make_kernel(version, clustersuffix)
    if 'tar_src' in funclist:
        tar_src(version, clustersuffix)
    if 'pull_src_tar' in funclist:
        pull_src_tar(version, nodelist, clustersuffix)
    if 'untar_src' in funclist:
        untar_src(version, nodelist, clustersuffix)
    if 'install_kernel' in funclist:
        install_kernel(version, nodelist, clustersuffix)
    if 'set_default_kernel' in funclist:
        set_default_kernel(version, nodelist, clustersuffix)
    if 'reboot' in funclist:
        reboot(nodelist, clustersuffix)
    if 'wait_for_alive' in funclist:
        wait_for_alive(nodelist, clustersuffix)
    if 'never_writeback' in funclist:
        never_writeback(nodelist, clustersuffix)
    if 'check_current_version' in funclist:
        check_current_version(nodelist, clustersuffix)
    if 'clean' in funclist:
        clean(nodelist, clustersuffix)
    if 'run_exp' in funclist:
        run_exp(version, jobtag, nodelist, clustersuffix, arg_usefinished)

if __name__ == '__main__':
    main()
    #print get_tar_version(sys.argv[1])
