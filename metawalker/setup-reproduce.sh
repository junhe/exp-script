
# check the permission of /mnt/scratch-sda4
# this makes sure the sda4 is full setup
#python runall.ssh.py 0-7 .noloop001.plfs 'ls -l /mnt|grep sda4' sync


# distribut images
#echo about to distribute images.... waiting for 5 sec
#sleep 5
#python lazy-build-from-ops.py 8.8.8 tag01 0-7 noloop001.plfs notusefinished distribute_images



# compile and install kernel
echo about to compile kernels.... waiting for 1 min
#sleep 60
python compile-kernel.py 3.5.0     0 noloop001.plfs download,make_oldconfig,make_kernel,install_kernel,set_default_kernel,reboot,wait_for_alive,never_writeback,check_current_version,clean  &
python compile-kernel.py 3.6.0-rc1 1 noloop001.plfs download,make_oldconfig,make_kernel,install_kernel,set_default_kernel,reboot,wait_for_alive,never_writeback,check_current_version,clean  &

wait
echo compilations are finished



