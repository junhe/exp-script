import subprocess

deblist = ['http://kernel.ubuntu.com/~kernel-ppa/mainline/v3.12.5-trusty/linux-headers-3.12.5-031205-generic_3.12.5-031205.201312120254_amd64.deb',
           'http://kernel.ubuntu.com/~kernel-ppa/mainline/v3.12.5-trusty/linux-headers-3.12.5-031205-generic_3.12.5-031205.201312120254_i386.deb',
           'http://kernel.ubuntu.com/~kernel-ppa/mainline/v3.12.5-trusty/linux-headers-3.12.5-031205_3.12.5-031205.201312120254_all.deb',
           'http://kernel.ubuntu.com/~kernel-ppa/mainline/v3.12.5-trusty/linux-image-3.12.5-031205-generic_3.12.5-031205.201312120254_amd64.deb',
           'http://kernel.ubuntu.com/~kernel-ppa/mainline/v3.12.5-trusty/linux-image-3.12.5-031205-generic_3.12.5-031205.201312120254_i386.deb']



def download(deblist):
    for deb in deblist:
        print deb
        subprocess.call(['wget', deb])

def install():
    subprocess.call('dpkg -i *.deb', shell=True)

if __name__ == '__main__':
    download(deblist)


