import subprocess

pre='node'
suf='.lustre3.ScalableFS'


def gethostname(index):
    return pre+str(index)+suf

def ssh_cmd(hostname, cmds):
    cmds = [str(x) for x in cmds]
    cmds = ' '.join(cmds)
    cmds = '"' + cmds + '"'
    print hostname, cmds
    #return
    subprocess.call(['ssh', hostname, 'bash', '-c', cmds])
    return

def setup_mds(mdt_dev):
    ssh_cmd(gethostname(0),
            ['sudo', 'mkfs.lustre','--fsname=temp',
                '--mgs','--mdt','--index=0',mdt_dev])
    ssh_cmd(gethostname(0),
            ['sudo', 'mount', '-t', 'lustre', mdt_dev, '/mnt/mds1'])

def setup_oss(hostindex, ostindex, ost_dev):
    nodename = gethostname(hostindex)
    mgsnode  = gethostname(0)
    ssh_cmd(nodename,
            ['sudo', 'mkfs.lustre','--fsname=temp',
                '--mgsnode='+mgsnode+'@tcp0', 
                '--ost', '--index='+str(ostindex), ost_dev])
    ssh_cmd(nodename,
            ['sudo', 'mount', '-t', 'lustre', ost_dev, '/mnt/ost1'])

def mount_lustre_on_client(nodename):
    ssh_cmd(nodename,
            ['sudo', 'mount', '-t', 'lustre', 
                "{host}@tcp0:/temp".format(host=gethostname(0)), '/mnt/lustre/'])


def built_lustre_cluster():
    dev = '/dev/sda'
    setup_mds(dev)
    for i in range(2):
        setup_oss(hostindex=i+1, ostindex=i, ost_dev=dev)
    mount_lustre_on_client(gethostname(3))

    ssh_cmd(gethostname(3),
            ['sudo', 'lfs', 'df', '-h'])

def umount_lustre():
    #umount clients
    ssh_cmd(gethostname(0)
            ['sudo','umount','/mnt/lustre'])
    for i in range(2):
        ssh_cmd(gethostname(i+1),
                ['sudo','umount','/mnt/ost1'])
    ssh_cmd(gethostname(0),
            ['sudo','umount','/mnt/mds1'])

built_lustre_cluster()
#umount_lustre()


