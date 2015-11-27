#!/usr/bin/bash

./run-workload.sh -j randr100_100iops.job -t temp
./run-workload.sh -j randrw9010_100iops.job -t temp
./run-workload.sh -j randrw8020_100iops.job -t temp
./run-workload.sh -j randrw7030_100iops.job -t temp
./run-workload.sh -j randrw6040_100iops.job -t temp
./run-workload.sh -j randrw5050_100iops.job -t temp
