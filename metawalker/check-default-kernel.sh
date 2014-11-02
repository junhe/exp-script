nodelist=$1
python ./runall.ssh.py $nodelist .noloop.plfs 'grep default /boot/grub/grub.cfg' sync

