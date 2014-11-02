
if [ "$#" -ne "3" ]; then
    echo "Usage: ./prepare-kernel.sh nodes clustersuffix releasename"
    echo "Example: ./prepare-kernel.sh 0-3 .noloop001.plfs myrelease"
    exit 1
fi

nodes=$1
suffix=$2
releasename=$3

echo nodes:  $nodes
echo suffix: $suffix

sleep 2

python runall.ssh.py $nodes $suffix 'cp -v ~/Home2/tars/config-3.12.5-ext4debug /usr/src/linux-3.12.5/.config' sync
python runall.ssh.py $nodes $suffix "python /users/jhe/workdir/exp-script/changekernelrelease.py /usr/src/linux-3.12.5/.config $releasename" sync

#python runall.ssh.py $nodes $suffix 'cp -v ~/Home2/patches/mballoc.patched.c /usr/src/linux-3.12.5/fs/ext4/mballoc.c' sync
#python runall.ssh.py $nodes $suffix 'cd /usr/src/linux-3.12.5/ && patch -p1 < /users/jhe/Home2/patches/goodnormalization.patch.3.12.5' sync
python runall.ssh.py $nodes $suffix 'cd /usr/src/linux-3.12.5/ && patch -p1 < /users/jhe/Home2/patches/nolastbig.3.12.5.patch' sync
#python runall.ssh.py $nodes $suffix 'cp -v ~/Home2/patches/mballoc.inumbertoprealloc.c /usr/src/linux-3.12.5/fs/ext4/mballoc.c' sync
sleep 10
#python runall.ssh.py $nodes $suffix 'cp -v ~/Home2/patches/mballoc.goodnorm.rmtail.c /usr/src/linux-3.12.5/fs/ext4/mballoc.c' sync
#python runall.ssh.py $nodes $suffix 'cp -v ~/Home2/patches/mballoc.nolastbig.goodnorm.rmtail.c /usr/src/linux-3.12.5/fs/ext4/mballoc.c' sync
#python runall.ssh.py $nodes $suffix 'cp -v ~/Home2/patches/mballoc.percpu0.nolastbig.goodnorm.rmtail.c /usr/src/linux-3.12.5/fs/ext4/mballoc.c' sync
#python runall.ssh.py $nodes $suffix 'cp -v ~/Home2/patches/mballoc.debug.percpu0.nolastbig.goodnorm.rmtail.c /usr/src/linux-3.12.5/fs/ext4/mballoc.c' sync


python runall.ssh.py $nodes $suffix 'cd /usr/src/linux-3.12.5/ && make -j3' async
python runall.ssh.py $nodes $suffix 'cd /usr/src/linux-3.12.5 && sudo make modules_install && sudo make install' async
python runall.ssh.py $nodes $suffix 'sudo python ~/workdir/exp_script/set-default-kernel.py 3.12.5debugext4' async
python runall.ssh.py $nodes $suffix "sudo python /users/jhe/workdir/exp-script/set-default-kernel.py $releasename" async
python runall.ssh.py $nodes $suffix 'sudo reboot' async


