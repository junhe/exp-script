import subprocess
import sys
# This program reboot machines with new kernel
# and check if they are up with the correct kernel


def set_default(entryname):
    f = open('/etc/default/grub', 'r')
    lines = f.readlines()
    f.close()

    f = open('/etc/default/grub', 'w')
    for line in lines:
        if line.startswith('GRUB_DEFAULT='):
            f.write('GRUB_DEFAULT=' + entryname + '\n')
        else:
            f.write(line)
    f.close()

def get_entryname(release):
    return "\"Previous Linux versions>Ubuntu, with Linux "+ release +"\""

def set_boot_default_release(release):
    entryname = get_entryname(release)
    set_default(entryname)
    subprocess.call(['update-grub'])

if __name__ == '__main__':
    if len( sys.argv ) != 2:
        print "usage:", sys.argv[0], 'release-name'
        print "example:", sys.argv[0], '3.6.0noloop'
        exit(1)
    ver = sys.argv[1]
    set_boot_default_release(ver)

