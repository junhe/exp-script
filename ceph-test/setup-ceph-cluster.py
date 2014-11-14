import subprocess
import os
import shlex

pre='node'
suf=''
lnetname='o2ib0'
allnodes=[0,1,2,3,4,5,6]
mdsnodes=[0]
ossnodes=[1,2]
clientnodes=[3,4,5,6]

def gethostname(index):
    return pre+str(index)+suf

def ssh_cmd(hostname, cmds):
    cmds = [str(x) for x in cmds]
    cmds = ' '.join(cmds)
    cmds = '"' + cmds + '"'
    c = ['ssh', hostname, 'bash', '-c', cmds]
    print ' '.join(c)
    return
    subprocess.call(c)
    return

def cmd(cmds):
    print ' '.join(cmds)
    return
    subprocess.call(cmds)

def setup_mds(nodeindex, mdt_dev):
    #ssh_cmd(gethostname(nodeindex),
            #['sudo', 'mkfs.lustre','--reformat','--fsname=temp',
                #'--mgs','--mdt','--index=0',mdt_dev])
    ssh_cmd(gethostname(nodeindex),
            ['sudo', 'mount', '-t', 'lustre', mdt_dev, '/mnt/mds1'])

def setup_oss(hostindex, ostindex, ost_dev):
    nodename = gethostname(hostindex)
    mgsnode  = gethostname(0)
    ssh_cmd(nodename,
            ['sudo', 'mkfs.lustre','--reformat','--fsname=temp',
                '--mgsnode='+mgsnode+'@'+lnetname, 
                '--ost', '--index='+str(ostindex), ost_dev])
    ssh_cmd(nodename,
            ['sudo', 'mount', '-t', 'lustre', ost_dev, '/mnt/ost1'])

def mount_lustre_on_client(nodename):
    ssh_cmd(nodename,
            ['sudo', 'mount', '-t', 'lustre', 
                ("{host}@"+lnetname+":/temp").format(host=gethostname(0)), 
                '/mnt/lustre/'])


def built_lustre_cluster():
    dev = '/dev/sda'

    # config lnet
    for nd in allnodes:
        ssh_cmd(gethostname(nd),
                #['echo', "''",
                ['echo', "'options lnet networks=o2ib0(ib0)'",
                #['echo', "'options lnet networks=tcp0(p29p2)'",
                #['echo', "'options lnet networks=o2ib0(ib0),tcp0(p29p1)'",
                    '|', 'sudo tee', '/etc/modprobe.d/lustre.conf'])

    for nd in mdsnodes:
        setup_mds(nd, dev)
    for i,nd in enumerate(ossnodes):
        setup_oss(hostindex=nd, ostindex=i, ost_dev=dev)

    for nd in clientnodes:
        mount_lustre_on_client(gethostname(nd))

    for nd in clientnodes:
        ssh_cmd(gethostname(nd),
                ['sudo chown jhe:ScalableFS -R /mnt/lustre'])
        ssh_cmd(gethostname(nd),
                ['sudo', 'lfs', 'df', '-h'])


def umount_lustre():
    #umount clients
    for nd in clientnodes:
        ssh_cmd(gethostname(nd),
            ['sudo','umount','/mnt/lustre'])
    for nd in ossnodes:
        ssh_cmd(gethostname(nd),
                ['sudo','umount','/mnt/ost1'])
    ssh_cmd(gethostname(0),
            ['sudo','umount','/mnt/mds1'])
    for nd in allnodes:
        ssh_cmd(gethostname(nd),
            ['sudo', 'lustre_rmmod'])


def build_ceph():
    # install ceph-deploy on admin-node
    cmd(['sudo', 'yum', 'install', '-y', 'ceph-deploy'])
    
    #create new monitor node
    cmd(['env CEPH_DEPLOY_TEST=YES ceph-deploy new', gethostname(1)])

    #config ceph
    if not os.path.exists('ceph.conf'):
        print 'not in the right directory'
        exit(1)
    
    with open('ceph.conf', 'a') as f:
        f.write('osd pool default size = 2')

    cmd(shlex.split(
        'env CEPH_DEPLOY_TEST=YES ceph-deploy install node0 node1 node2 node3'))

    cmd(shlex.split('env CEPH_DEPLOY_TEST=YES ceph-deploy mon create-initial'))    
    
    ssh_cmd(gethostname(2),
            ['sudo mkdir /var/local/osd0'])
    ssh_cmd(gethostname(3),
            ['sudo mkdir /var/local/osd1'])

    cmd(shlex.split(
        'env CEPH_DEPLOY_TEST=YES ceph-deploy osd prepare '\
        'node2:/var/local/osd0 node3:/var/local/osd1'))
    cmd(shlex.split(
        'env CEPH_DEPLOY_TEST=YES ceph-deploy osd activate '
        'node2:/var/local/osd0 node3:/var/local/osd1'))
    cmd(shlex.split(
        'env CEPH_DEPLOY_TEST=YES ceph-deploy admin '
        'node0 node1 node2 node3'))
    cmd(shlex.split(
        'sudo chmod +r /etc/ceph/ceph.client.admin.keyring'))

    cmd(shlex.split(
        'ceph health'))

build_ceph()





