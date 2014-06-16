nodelist=$1
nodesuffix=$2
basever=$3
releasename=$4

# install kernel
python ./runall.ssh.py $nodelist $nodesuffix "cd ~/Home2/tars/linux-$basever/; sudo make modules_install; sudo make install" sync

# set default kernel
python ./runall.ssh.py $nodelist $nodesuffix "sudo python ~/bin/set-default-kernel.py $releasename" sync

# check default kernel
python ./runall.ssh.py $nodelist $nodesuffix 'grep default= /boot/grub/grub.cfg' sync

# reboot
echo we are about to reboot.. in 5 sec
sleep 5
python ./runall.ssh.py $nodelist $nodesuffix 'sudo reboot' sync

