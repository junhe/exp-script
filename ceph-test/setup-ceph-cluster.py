import optparse
import sys
import subprocess
import os
import shlex
import time

pre='node'
suf=''
lnetname='o2ib0'
allnodes=[0,1,2,3,4,5,6]
mdsnodes=[0]
ossnodes=[1,2]
clientnodes=[3,4,5,6]


parser = optparse.OptionParser()
parser.add_option('--showonly', action='store_true', default=False)
parser.add_option('--actions', action='store', dest='actions',
        default='yuminstall,new,cephconf,install,mon,prepare,active,admin,health',
        help   ='sudoers,yuminstall,new,cephconf,install,mon,prepare,active,admin,health')
opts = parser.parse_args(sys.argv[1:])[0]
print opts
time.sleep(2)

def gethostname(index):
    return pre+str(index)+suf

def ssh_cmd(hostname, cmds, wrapper='"'):
    cmds = [str(x) for x in cmds]
    cmds = ' '.join(cmds)
    cmds = wrapper + cmds + wrapper
    c = ['ssh', hostname, 'bash', '-c', cmds]
    print ' '.join(c)
    print c

    if opts.showonly == True:
        return

    ret = subprocess.call(c)
    if ret != 0:
        print 'error when executing:', ' '.join(c)
        exit(1)
    return

def cmd(cmds):
    print ' '.join(cmds)

    if opts.showonly == True:
        return

    ret = subprocess.call(cmds)
    if ret != 0:
        print 'error when executing:', ' '.join(cmds)
        exit(1)
    return  

def build_ceph(action):
    # set sudoers
    if action == 'sudoers':
        for i in [0,1,2,3]:
            ssh_cmd(gethostname(i),
                    ['echo Defaults env_keep = \\\"http_proxy https_proxy ftp_proxy\\\"|sudo tee -a /etc/sudoers'],
                    wrapper="'")
        return

    #install ceph-deploy on admin-node
    if action == 'yuminstall':
        cmd(['sudo', 'yum', 'install', '-y', 'ceph-deploy'])
        return
    
    #create new monitor node
    if action == 'new':
        cmd(['env', 'CEPH_DEPLOY_TEST=YES', 'ceph-deploy', 'new', gethostname(1)])
        return

    #config ceph
    if action == 'cephconf':
        if not os.path.exists('ceph.conf'):
            print 'not in the right directory'
            exit(1)
        
        with open('ceph.conf', 'a') as f:
            f.write('osd pool default size = 2')
        return

    if action == 'install':
        cmd(shlex.split(
            'env CEPH_DEPLOY_TEST=YES ceph-deploy install node0 node1 node2 node3'))
        return
    
    if action == 'mon':
        cmd(shlex.split('env CEPH_DEPLOY_TEST=YES ceph-deploy  --overwrite-conf mon create-initial'))    
        return
    
    if action == 'prepare':
        ssh_cmd(gethostname(2),
                ['if [ ! -d /var/local/osd0 ]; then sudo mkdir /var/local/osd0; fi'])
        ssh_cmd(gethostname(3),
                ['if [ ! -d /var/local/osd1 ]; then sudo mkdir /var/local/osd1; fi'])

        cmd(shlex.split(
            'env CEPH_DEPLOY_TEST=YES ceph-deploy osd prepare '\
            'node2:/var/local/osd0 node3:/var/local/osd1'))
        return

    if action == 'active':
        cmd(shlex.split(
            'env CEPH_DEPLOY_TEST=YES ceph-deploy osd activate '
            'node2:/var/local/osd0 node3:/var/local/osd1'))
        return

    if action == 'admin':
        cmd(shlex.split(
            'env CEPH_DEPLOY_TEST=YES ceph-deploy --overwrite-conf admin '
            'node0 node1 node2 node3'))
        cmd(shlex.split(
            'sudo chmod +r /etc/ceph/ceph.client.admin.keyring'))
        return

    if action == 'health':
        cmd(shlex.split(
            'sleep 4'))
        cmd(shlex.split(
            'ceph health'))
        return

    print 'action', action, 'not registered'
    exit(1)

def main():
    #build_ceph()
    for x in opts.actions.split(','):
        build_ceph(action=x)

if __name__ == '__main__':
    main()

