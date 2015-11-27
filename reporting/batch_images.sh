#!/usr/bin/bash

./fio_collector.py -p no-dmcache/build-949-std/randr100_100iops -k 'mixed/clat/percentile/95.000000' -t "FIO 100% random 8k READ - no dmcache (1 job = 100IOPS) build-949 non-sharded" -o "randr100_100iops-no-dmcache-b949-nonsharded.png"
#
./fio_collector.py -p no-dmcache/build-949-std/randrw9010_100iops -k 'mixed/clat/percentile/95.000000' -t "FIO 90:10 random 8k r:w  - no dmcache (1 job = 100IOPS) build-949 non-sharded" -o "randrw9010_100iops-no-dmcache-b949-nonsharded.png"
#
./fio_collector.py -p no-dmcache/build-949-std/randrw8020_100iops -k 'mixed/clat/percentile/95.000000' -t "FIO 80:20 random 8k r:w  - no dmcache (1 job = 100IOPS) build-949 non-sharded" -o "randrw8020_100iops-no-dmcache-b949-nonsharded.png"
#
./fio_collector.py -p no-dmcache/build-949-std/randrw7030_100iops -k 'mixed/clat/percentile/95.000000' -t "FIO 70:30 random 8k r:w  - no dmcache (1 job = 100IOPS) build-949 non-sharded" -o "randrw7030_100iops-no-dmcache-b949-nonsharded.png"
#
./fio_collector.py -p no-dmcache/build-949-std/randrw6040_100iops -k 'mixed/clat/percentile/95.000000' -t "FIO 60:40 random 8k r:w  - no dmcache (1 job = 100IOPS) build-949 non-sharded" -o "randrw6040_100iops-no-dmcache-b949-nonsharded.png"
#
./fio_collector.py -p no-dmcache/build-949-std/randrw5050_100iops -k 'mixed/clat/percentile/95.000000' -t "FIO 50:50 random 8k r:w  - no dmcache (1 job = 100IOPS) build-949 non-sharded" -o "randrw5050_100iops-no-dmcache-b949-nonsharded.png"
