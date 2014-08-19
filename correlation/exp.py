import pprint
import subprocess

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

def create_file( extlist ):
    conv_args = get_convertor_args(extlist)


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
    maxlogical = 0
    nblocks = 0
    for ext in extlist:
        m = ext['logical_block_num'] + ext['length']
        nblocks += ext['length']
        if m > maxlogical:
            maxlogical = m
    print maxlogical, maxlogical*4096, nblocks
    
    cmd = ['debugfs', dev, '-w', '-R', 'mi '+filespec]
    print cmd

    fields = [''] * 31

    # size
    fields[3] = maxlogical*4096

    # block count high
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


def main():
    # create file
    cmd = ['touch', '/mnt/scratch/myfile']
    subprocess.call(cmd)
    subprocess.call('sync')

    dev = '/dev/loop0'
    mountpoint = '/mnt/scratch'
    args = [2,
            0,1,65535,
            1,1,65550]
    extlist = create_extent_list(args) 
    if is_extentlist_is_use(dev, extlist):
        print 'a requested extent is not free'
        exit(1)
    set_extlist_as_used(dev, extlist)
    
    set_iblocks(dev, 'myfile', extlist)
    remount_dev(dev, mountpoint)

if __name__ == '__main__':
    main()





