#!/bin/bash

#do the following first
#modprobe lnet_selftest
export LST_SESSION=$$
lst new_session read/write
lst add_group servers node0-dib@o2ib0
lst add_group readers node0-dib@o2ib0
lst add_group writers node0-dib@o2ib0
lst add_batch bulk_rw
lst add_test --batch bulk_rw --from readers --to servers \
brw read check=simple size=1M
lst add_test --batch bulk_rw --from writers --to servers \
brw write check=full size=4K
# start running
lst run bulk_rw
# display server stats for 30 seconds
lst stat servers & sleep 30; kill $!
# tear down
lst end_session

