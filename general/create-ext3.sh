#!/bin/bash - 

set -o nounset                              # Treat unset variables as an error

mountpoint=/mnt/scratch-sda4
dev=/dev/sda4
who=jhe:FSPerfAtScale

sudo mkdir $mountpoint
sudo mkfs.ext3 -b 4096 $dev 
sudo mount $dev $mountpoint
sudo chown -R $who $mountpoint
sudo bash -c "echo $dev $mountpoint auto defaults 0 2 >> /etc/fstab"
