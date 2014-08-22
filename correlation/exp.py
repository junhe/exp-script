import pprint
import random
import os
import subprocess

def get_quantile(objlist, ratio):
    """
    ratio: recommended [0,1), but you can do [0,1] (change the code)
    index: [0,n-1]
    """
    if ratio == 1:
        print 'having ratio==1 will make it biased toward the last object'
        return None
    # consider this is a rod of length n
    # imagine it consists of segments of size 1
    n = len(objlist)
    if n == 0:
        return None
    # this is the length of the first rod if you cut it into two rods at ratio
    cutlength = n*ratio
    index = int(cutlength) #this is the index of the segment it falls into
    return objlist[index]

def pick_k_objects(objlist, k):
    """
    This function return a list of k objects.
    The returned list is like [objlist[0], ... objlist[n-1]]
    """
    n = len(objlist)
    retlist =  []
    for i in range(k):
        j = i*(n-1)/(k-1) 
        retlist.append( objlist[j] )
    return retlist

def get_empty_ext():
    dict = { 
            'logical_block_num':None,
            'length'           :None,
            'physical_block_num':None
            }
    return dict

def create_extent_list( argv ):
    "argv is the input of convertor"
    nExt = int(argv[0])

    extlist = []
    for i in range(nExt):
        ext = get_empty_ext()
        ext['logical_block_num']  = argv[3*i+1]
        ext['length']             = argv[3*i+2]
        ext['physical_block_num'] = argv[3*i+3]
        extlist.append(ext)

    return extlist

def get_convertor_args( extlist ):
    nExt = len(extlist)

    args = [nExt]
    for ext in extlist:
        args.append(ext['logical_block_num'])
        args.append(ext['length'])
        args.append(ext['physical_block_num'])
    
    rest = 4 - nExt
    for i in range(rest):
        args.extend([0,0,0])

    return args

def get_i_block_int(extlist):
    args = get_convertor_args(extlist)
    
    cmd = ['./convertor'] + args
    cmd = [str(x) for x in cmd]
    print(cmd)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    proc.wait()
    
    lines = []
    for line in proc.stdout:
        lines.append(line.strip())
    
    iblocks = [int(x) for x in lines]
    return iblocks

def do_debugfs(dev, subcmd):
    subcmd = [str(x) for x in subcmd]
    #if len(subcmd) > 1:
        #subcmd[1] = '"' + subcmd[1]
        #subcmd[-1] = subcmd[-1] + '"'

    cmd = ['debugfs', dev, '-w', '-R', ' '.join(subcmd)]
    print cmd
    proc = subprocess.Popen(cmd, 
                    stdin =subprocess.PIPE,    
                    stdout=subprocess.PIPE)
    proc.wait()
    if proc.returncode != 0:
        print 'error doing debugfs'
        exit(1)
    return proc

def do_set_inode_field(dev, filespec, field, value):
    cmd = ['set_inode_field',
           filespec,
           field, 
           value]
    do_debugfs(dev, cmd)

def is_block_in_use(dev, block, count):
    "test if any block in block,count is in use"
    subcmd = ['testb', block, count]
    subcmd = [str(x) for x in subcmd]

    cmd = ['debugfs', dev, '-w', '-R', ' '.join(subcmd)]
    print cmd
    proc = subprocess.Popen(cmd,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE)
    proc.wait()

    for line in proc.stdout:
        if "marked in use" in line:
            return True
    return False

def is_extent_in_use(dev, ext):
    return is_block_in_use(dev, 
                           ext['physical_block_num'],
                           ext['length'])

def is_extentlist_is_use(dev, extlist):
    for ext in extlist:
        if is_extent_in_use(dev, ext):
            print ext, 'is in use'
            return True
    return False

def setb(dev, block, count):
    cmd = ['setb', block, count]
    proc = do_debugfs(dev, cmd)
    print proc.communicate()[0]
    return proc.returncode

def set_ext_as_used(dev, ext):
    return setb(dev, ext['physical_block_num'], ext['length'])

def set_extlist_as_used(dev, extlist):
    for ext in extlist:
        set_ext_as_used(dev, ext)

def freeb(dev, block, count):
    cmd = ['freeb', block, count]
    proc = do_debugfs(dev, cmd)
    print proc.communicate()[0]
    return proc.returncode

def set_ext_as_unused(dev, ext):
    return freeb(dev, ext['physical_block_num'], ext['length'])

def set_extlist_as_unused(dev, extlist):
    for ext in extlist:
        set_ext_as_unused(dev, ext)


def get_ext_stat(extlist):
    # find out file size
    maxlogical = 0
    nblocks = 0
    for ext in extlist:
        m = ext['logical_block_num'] + ext['length']
        nblocks += ext['length']
        if m > maxlogical:
            maxlogical = m
    return {'filesize': maxlogical*4096,
            'nblocks' : nblocks}

def set_iblocks(dev, filespec, extlist):
    """
                          Mode    [0100644]
                       User ID    [10083]
                      Group ID    [6010]
                          Size    [17920884]
                 Creation time    [1408382615]
             Modification time    [1408382615]
                   Access time    [1408382305]
                 Deletion time    [0]
                    Link count    [1]
              Block count high    [0]
                   Block count    [35008]
                    File flags    [0x80000]
                    Generation    [0x4b11e8e1]
                      File acl    [0]
           High 32bits of size    [0]
              Fragment address    [0]
               Direct Block #0    [2]
               Direct Block #1    [2]
               Direct Block #2    [2]
               Direct Block #3    [0]
               Direct Block #4    [5]
               Direct Block #5    [65535]
               Direct Block #6    [0]
               Direct Block #7    [0]
               Direct Block #8    [0]
               Direct Block #9    [0]
              Direct Block #10    [0]
              Direct Block #11    [2]
                Indirect Block    [0]
         Double Indirect Block    [0]
         Triple Indirect Block    [0]
    """
    iblocks = get_i_block_int(extlist)

    # find out file size
    stat = get_ext_stat(extlist)
    
    cmd = ['debugfs', dev, '-w', '-R', 'mi '+filespec]
    print cmd

    fields = [''] * 31

    # size
    fields[3] = stat['filesize']

    # block count high
    nblocks = stat['nblocks']*8 # we need sector count here
    fields[9] = (nblocks & 0xffffffff00000000) >>32
    # block count low
    fields[10] = nblocks & 0xffffffff

    # iblocks
    iblocks = [str(x) for x in iblocks]
    for i,value in enumerate(iblocks):
        fields[16+i] = value
    fields = [str(x)+'\n' for x in fields]
    fieldstr = ''.join(fields)
    print fieldstr

    proc = subprocess.Popen(cmd, 
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE)
    proc.communicate(input=fieldstr)
    proc.wait()
    
    if proc.returncode == 0:
        print 'iblocks are set'
    else:
        print 'failed to set iblocks'
        exit(1)

def remount_dev(dev, mountpoint):
    "sudo umount /dev/loop0 && sudo mount /dev/loop0 /mnt/scratch"
    cmd = ['umount', dev]
    subprocess.call(cmd)

    cmd = ['mount', dev, mountpoint]
    subprocess.call(cmd)

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

def create_big_file():
    f = open("/boot/initrd.img-3.12.5", 'r')
    buf = f.read(2**20)
    f.close()

    f = open("/tmp/bigs2", "w")
    for i in range(128):
        f.write(buf)
    f.close()

def get_block_list_humanpick():
    groupsize = 128*2**20
    ngroups = 14802+1 #2TB disk
    distances = [(2**x)/4096 for x in range(12, 40, 4)] #in block
    start = ((ngroups/2) * groupsize)/4096
    
    pairs = [[start, start+x] for x in distances]
    return pairs

def get_block_list(npick):
    groupsize = 128*2**20
    #disksize = 1909583652*1024 # 1.8TB
    #ngroups = disksize/(128*(2**20)) 
    ngroups = 14802+1 #2TB disk
    print 'ngroups', ngroups

    exps = range(int(math.log(ngroups, 2)))
    groups = [2**i for i in exps]
    print 'groups',groups

    #groups = pick_k_objects(range(ngroups), npick)
    blocklist = [(groupno * groupsize + groupsize/2)/4096 
                    for groupno in groups]
    print blocklist
    return blocklist

def sample_with_replace(seq, k):
    ret = [random.choice(seq) for i in range(k)]
    return ret

def groupno_to_block(groupno):
    groupsize = 128*2**20
    return (groupno * groupsize + groupsize/2)/4096 

def get_block_random_pairs(npick):
    groupsize = 128*2**20
    ngroups = 14802+1 #2TB disk
    print 'ngroups', ngroups

    groupslist = range(ngroups)
    groups = [sorted(sample_with_replace(groupslist,2))
                for i in range(npick)]
    blockpairs = [[groupno_to_block(x),groupno_to_block(y)]
                    for x,y in groups]

    blockpairs2 = [[groupno_to_block(x),groupno_to_block(x)]
                    for x,y in groups]

    ret_pairs = blockpairs + blockpairs2
    print ret_pairs
    return ret_pairs

def filefrag(filepath):
    cmd = ['filefrag', '-sv', filepath]
    subprocess.call(cmd)

def create_file(dev, mountpoint, filename, extlist):
    "create a new file" 

    remount_dev(dev, mountpoint)

    path = os.path.join(mountpoint, filename)
    if os.path.exists(path):
        print 'deleting', path
        delete_file(dev, mountpoint, filename)
        subprocess.call(['sync'])
    set_extlist_as_unused(dev, extlist) # 

    remount_dev(dev, mountpoint)


    if is_extentlist_is_use(dev, extlist):
        print 'a requested extent is not free'
        exit(1)
    set_extlist_as_used(dev, extlist)
    
    print 'touching', filename
    cmd = ['touch', os.path.join(mountpoint, filename)]
    subprocess.call(cmd)
    subprocess.call('sync')

    set_iblocks(dev, filename, extlist)
    remount_dev(dev, mountpoint)

def delete_file(dev, mountpoint, filename):
    path = os.path.join(mountpoint, filename)
    cmd = ['rm', '-f', path]
    ret = subprocess.call(cmd)
    print cmd, ret
    
    cmd = ['sync']
    ret = subprocess.call(cmd)
    print cmd, ret

def run_exp(mode, mountpoint, filename, size, info=None):
    if info == None:
        header = ' '
        datas = ' '
    else:
        header = ' '.join(info.keys())
        datas = [str(x) for x in info.values()]
        datas = ' '.join(datas)

    cmd = ['./perform', mode, os.path.join(mountpoint, filename), size,
           header, datas ]
    cmd = [str(x) for x in cmd]
    print cmd
    subprocess.call(cmd)

def clean_all_cache(dev, mountpoint):
    print 'cleanging caches...'
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

def exp_main_pairs():
    #blocklist = get_block_pairs(16)
    #blocklist = get_block_list_humanpick()
    blocklist = get_block_random_pairs(1024)
    dev = '/dev/sda4'
    mountpoint = '/mnt/scratch'
    filename = 'testfile'


    for size in [1]:
        for blockpair in blocklist:
            ext_start = get_empty_ext()
            ext_start['logical_block_num'] = 0 
            ext_start['length'] = size
            if blockpair[0] == blockpair[1]:
                ext_start['physical_block_num'] = blockpair[0]-size
            else:
                ext_start['physical_block_num'] = blockpair[0]

            ext_end = get_empty_ext()
            ext_end['logical_block_num'] = size
            ext_end['length'] = size
            ext_end['physical_block_num'] = blockpair[1]

            extlist = [ext_start, ext_end]
            print extlist

            create_file(dev, mountpoint, filename, extlist)
            filefrag(os.path.join(mountpoint, filename))
            
            info = {'extsize':size,
                    'nextents': len(extlist),
                    'distance'   :extlist[-1]['physical_block_num'] -
                        (extlist[0]['physical_block_num']+extlist[0]['length']),
                    'startblock': extlist[0]['physical_block_num'],
                    'endblock'  : extlist[1]['physical_block_num']
                    }

            filesize = get_ext_stat(extlist)['filesize']

            for rep in range(5):
                clean_all_cache(dev, mountpoint)
                remount_dev(dev, mountpoint)
                run_exp('w', mountpoint, filename, filesize, info)

                clean_all_cache(dev, mountpoint)
                remount_dev(dev, mountpoint)
                run_exp('r', mountpoint, filename, filesize, info)


def exp_main():
    blocklist = get_block_list(16)
    dev = '/dev/sda4'
    mountpoint = '/mnt/scratch'
    filename = 'testfile'


    for rep in range(4):
        for size in [1, 4, 16, 64]:
            ext_start = get_empty_ext()
            ext_start['logical_block_num'] = 0 
            ext_start['length'] = size
            ext_start['physical_block_num'] = blocklist[0] - size

            for block in blocklist:
                ext_end = get_empty_ext()
                ext_end['logical_block_num'] = size
                ext_end['length'] = size
                ext_end['physical_block_num'] = block

                extlist = [ext_start, ext_end]
                print extlist

                create_file(dev, mountpoint, filename, extlist)
                filefrag(os.path.join(mountpoint, filename))
                
                info = {'extsize':size,
                        'nextents': len(extlist),
                        'distance'   :extlist[-1]['physical_block_num'] -
                            (extlist[0]['physical_block_num']+extlist[0]['length'])}

                filesize = get_ext_stat(extlist)['filesize']
                run_exp('w', mountpoint, filename, filesize, info)
                clean_all_cache(dev, mountpoint)
                remount_dev(dev, mountpoint)
                run_exp('r', mountpoint, filename, filesize, info)

def exp_main_nextents():
    blocklist = get_block_list()
    dev = '/dev/sda4'
    mountpoint = '/mnt/scratch'
    filename = 'testfile'

    #blocklist = blocklist[0:8]
    print len(blocklist)
    print blocklist

    nfileblocks = 4
    for nextents in range(1, 5):
        # make extent list
        print nextents, 'extent per file'
        extlist = []
        #extblocks = int(nfileblocks/nextents)
        extblocks = 1
        for i in range(nextents):
            ext = get_empty_ext()
            ext['logical_block_num']=i * extblocks
            ext['length'] = extblocks
            listsize = len(blocklist)
            if nextents == 1:
                listi = 0
            else:
                #print 'i/float(nextents-1)', i/float(nextents-1)
                listi = int( (listsize-1)* (i/float(nextents-1)) )
            print 'listi', listi, 'listsize', listsize
            ext['physical_block_num'] = blocklist[listi]
            extlist.append(ext)
        pprint.pprint(extlist)

        create_file(dev, mountpoint, filename, extlist)
        filefrag(os.path.join(mountpoint, filename))
        
        filesize = get_ext_stat(extlist)['filesize']
        run_exp('w', mountpoint, filename, filesize)
        clean_all_cache(dev, mountpoint)
        remount_dev(dev, mountpoint)
        run_exp('r', mountpoint, filename, filesize)


if __name__ == '__main__':
    #main()
    #mkext4('/dev/sda4', '/mnt/scratch')
    #exp_main()
    #exp_main_nextents()
    #create_big_file()
    #get_block_pairs(3)
    #print get_block_list_humanpick()
    exp_main_pairs()





