import subprocess
import os
import sys
import random
import itertools

def ParameterCominations(parameter_dict):
    """
    Get all the cominbation of the values from each key
    http://tinyurl.com/nnglcs9

    Input: parameter_dict={
                    p0:[x, y, z, ..],
                    p1:[a, b, c, ..],
                    ...}
    Output: [
             {p0:x, p1:a, ..},
             {..},
             ...
            ]
    """
    d = parameter_dict
    return [dict(zip(d, v)) for v in itertools.product(*d.values())]

def mkext4(dev, mountpoint):
    ret = subprocess.call(['umount', dev])
    print 'umount', ret
    
    bytes = 2**40
    blockcount = bytes/4096
    cmd = ['mkfs.ext4', '-b', '4096', 
            '-E', 'lazy_itable_init=0',
            dev]
    cmd = [str(x) for x in cmd]
    print cmd
    ret = subprocess.call(cmd)
    print cmd, ret

    if not os.path.exists(mountpoint):
        os.makedirs(mountpoint)

    cmd = ['mount', dev, mountpoint]
    ret = subprocess.call(cmd)
    print cmd, ret
            
    cmd = ['chown', '-R', 'jhe:plfs', mountpoint]
    ret = subprocess.call(cmd)
    print cmd, ret


def remount_dev(dev, mountpoint):
    "sudo umount /dev/loop0 && sudo mount /dev/loop0 /mnt/scratch"
    cmd = ['umount', dev]
    subprocess.call(cmd)

    cmd = ['mount', dev, mountpoint]
    subprocess.call(cmd)

def create_big_file():
    f = open("/boot/initrd.img-3.12.5", 'r')
    buf = f.read(2**20)
    f.close()

    f = open("/tmp/bigs2", "w")
    for i in range(128):
        f.write(buf)
    f.close()

def clean_all_cache(dev, mountpoint):
    #print 'cleanging caches...'
    subprocess.call(['sync'])
    cmd = "echo 3 > /proc/sys/vm/drop_caches"
    subprocess.call(cmd, shell=True)

    if not os.path.exists('/tmp/bigs2'):
        create_big_file()
    cmd = "cp /tmp/bigs2 "+mountpoint
    ret = subprocess.call(cmd, shell=True)
    if ret != 0:
        print cmd, 'failed'
        exit(1)

    subprocess.call(['sync'])
    cmd = "echo 3 > /proc/sys/vm/drop_caches"
    subprocess.call(cmd, shell=True)

    cmd = "mv "+mountpoint+"/bigs2 /tmp/bigs3"
    ret = subprocess.call(cmd, shell=True)
    if ret != 0:
        print cmd, 'failed'
        exit(1)

    subprocess.call(['sync'])
    cmd = "echo 3 > /proc/sys/vm/drop_caches"
    subprocess.call(cmd, shell=True)


headerprinted = False
def run_exp(conf):
    global headerprinted

    exe = './seqorrandom'
    cmd = [exe, conf['filepath'], 
                conf['chunksize'], 
                conf['nchunks'],
                conf['mode'],
                conf['pattern']
                ]
    cmd = [str(x) for x in cmd]
    #print 'doing', cmd
    
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    proc.wait()
    for line in proc.stdout:
        if 'DATAROWMARKER' in line:
            print line,
        if 'MYHEADERROWMARKER' in line and headerprinted == False:
            print line,
            headerprinted = True
        sys.stdout.flush()


def main():
    filesize = [x*(2**20) for x in [4]]
    nlist = [2**x for x in range(0, 11, 2)]
    
    chunksize_list = []
    nchunks_list = []
    for fsize in filesize:
        for nchunks in nlist:
            nchunks_list.append(nchunks)
            chunksize = fsize/nchunks
            chunksize_list.append(chunksize)
            print fsize, nchunks, chunksize


    paras = {
        'filepath'       :['/mnt/scratch/testfile'],
        'chunksize'      :chunksize_list,
        'nchunks'        :nchunks_list,
        'pattern'        :['s','r']
        }

    #paras = {
        #'filepath'       :['/mnt/scratch/testfile'],
        ##'chunksize'      :[2**x for x in range(10, 21)],
        #'chunksize'      :[4096],
        ##'nchunks'        :[2**x for x in range(0, 10, 2)],
        #'nchunks'        :[1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024],
        #'pattern'        :['s','r']
        #}

    #print paras

    paralist = ParameterCominations(paras)
    paralist = paralist * 5
    random.shuffle(paralist)

    for conf in paralist:
        clean_all_cache('/dev/sda4', '/mnt/scratch')
        conf['mode'] = 'w'
        run_exp(conf)

        clean_all_cache('/dev/sda4', '/mnt/scratch')
        conf['mode'] = 'r'
        run_exp(conf)

if __name__ == '__main__':
    mkext4('/dev/sda4', '/mnt/scratch')
    main()




