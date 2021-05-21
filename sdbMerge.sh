#!/bin/sh
inotifywait -m -r -e move -e create --format '%w%f' "/opt/SA/sdb/Schedule" | while read f
do
    # python3 /opt/SA/script/sdbMerge.py "/opt/SA/sdb/Schedule/schedule" $f
    python3 sdbMerge.py "/opt/SA/sdb/schedule" $f
done