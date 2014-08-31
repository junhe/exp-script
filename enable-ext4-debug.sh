#!/bin/bash - 
#===============================================================================
#
#          FILE: enable-ext4-debug.sh
# 
#         USAGE: ./enable-ext4-debug.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: 07/20/14 22:41:45 EDT
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error
echo 1 | sudo tee /sys/module/ext4/parameters/mballoc_debug

