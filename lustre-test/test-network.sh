#!/bin/bash
export LST_SESSION=$$
lst new_session read/write
lst add_group servers 10.51.1.15@tcp0
lst add_group readers 10.51.1.15@tcp0
lst add_group writers 10.51.1.15@tcp0
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

