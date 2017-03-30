# fio-tools
This project contains some tools to make measuring performance with fio a little easier when working with gluster and ovirt. The goal is to use fio to benchmark latencies within vm's and then use the fio results as input to matplotlib.pylot, to simplify the interpretation of the results.  
  

## Pre-Requisites  
+ Use a node to act as the test controller - this can be your desktop
+ clone this repo to your controller node
+ your controller will need python2-matplotlib,python2-numpy, nmap-ncat
+ have passwordless ssh setup between your controller and the test vm's  
+ have passwordless ssh setup between your controller and the gluster nodes
+ ensure fio is installed on your controller and each vm (*NB. use the same versions!*)
+ on each vm install, enable and start the fio-server.service (from this repo's systemd directory)  
+ ensure that port 8765 is open on each vm

### Tested Versions
Hypervisors : RHEL 7.3, Glusterfs 3.8.4   
VM's: RHEL 7, fio 2.1.7  
Controller: F25, fio 2.1.7  

fio version can be found at http://rpm.pbone.net/index.php3/stat/4/idpl/26433361/dir/redhat_el_7/com/fio-2.1.7-1.el7.rf.x86_64.rpm.html  
If you're using a Fedora as the controller, installing the same rpm as RHEL is fine.

NB. As of March 2017, the fio version in EPEL (2.2.8-1 and 2.2.8-2) seem prone to intermittent crc payload issues when running fio in client/server mode. 

## Workflow
For best results, evenly distribute the vm's across the hypervisors  
  
The repo is split into two main steps; run the workload -> summarise the workload, with a pretty chart :)

### Running the workload
From the root of the repository
1. ```cd controller```
2. update run-workload.yml, defining your gluster hosts and clients (vm's)
3. create an fio job file (some examples are provided in the repo)
4. execute the run-workload.sh script  
```markdown
e.g
./run-workload.sh -j randrw7030.job -t ssd_data -r 120 -q 8 
```
In the above example, the randrw7030.job is sent to all defined clients, which are backed by the gluster volume called 'ssd_data'. Overrides for qdepth and runtime are provided allowing the fio job file to be standard across different runs.  
By default, the workload is be run in a 'cumulative' manner(stepped), increasing the number of concurrent vm's executing the fio workload, one by one. You can use the -m immediate parameter if you just want to see the results for a single iteration of a given number of clients (as defined in run-workload.yaml).

Output is generated to a default 'output' sub-directory, or you may specify the -o option to direct it to another location. The output directory will hold;  
+ the fio json files from each client
+ a copy of the actual fio job file used (after the runtime changes are made)
+ a copy of the volume configuration (vol info)
+ gluster vol profiles for each test cycle [optional if you use the -s parameter]

### Interpreting the Output
Once the run is complete, you can use the json data to create a chart
1. cd ```../reporting```
2. run the gencharts.py program to create the chart from the json data (-p points to the path location of the fio json files - normally the same dir as the -o option used by run-workload.sh)
```markdown
./genchart.py -p ~/Downloads/7030_4 -t "NVME - Random R/W 70:30 4k I/O" \
 -s "qdepth=8, 16GB data/vm" -o output/myfile.png
```  
3. genchart.py will create a csv dump of the summary data, and also provide a chart that plots read and write i/o latencies against the IOPS for the different densities of vm's. 

eg.
```markdown
[paul@work reporting]$ ./genchart.py -p ../controller/7030_6/ -t 'NVMe Bricks - FIO Random R/W 4K 70:30 Workload' -s '(qdepth=8, 16GB testdata per vm)'
processing file ../controller/7030_6/randrw7030.job_ssd_data_001_json.out
processing file ../controller/7030_6/randrw7030.job_ssd_data_002_json.out
processing file ../controller/7030_6/randrw7030.job_ssd_data_003_json.out
processing file ../controller/7030_6/randrw7030.job_ssd_data_004_json.out
processing file ../controller/7030_6/randrw7030.job_ssd_data_005_json.out
processing file ../controller/7030_6/randrw7030.job_ssd_data_006_json.out
processing file ../controller/7030_6/randrw7030.job_ssd_data_007_json.out
processing file ../controller/7030_6/randrw7030.job_ssd_data_008_json.out
processing file ../controller/7030_6/randrw7030.job_ssd_data_009_json.out
processing file ../controller/7030_6/randrw7030.job_ssd_data_010_json.out
processing file ../controller/7030_6/randrw7030.job_ssd_data_011_json.out
processing file ../controller/7030_6/randrw7030.job_ssd_data_012_json.out
processing file ../controller/7030_6/randrw7030.job_ssd_data_013_json.out
processing file ../controller/7030_6/randrw7030.job_ssd_data_014_json.out
processing file ../controller/7030_6/randrw7030.job_ssd_data_015_json.out

title, NVMe Bricks - FIO Random R/W 4K 70:30 Workload
subtitle, (qdepth=8, 16GB testdata per vm)
xaxis labels,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
read iops,3223,6492,11292,12436,13244,13937,13951,13943,14063,14022,14049,13889,13740,13701,13655
write iops,1380,2780,4836,5327,5674,5970,5978,5976,6025,6009,6015,5944,5887,5869,5848
read latency (μs),1192,1232,1293,1556,1736,1864,2137,2372,2501,2787,2962,3186,3452,3725,3909
write latency (μs),5216,5088,4021,5408,6403,7008,8685,10000,10844,12377,13701,14826,16443,17801,18969


Summary Statistics
	Number of job files: 15
	Number of Clients  : 15
	Total IOPS         : 19503
	AVG reads/VM       : 910.333333333 (std=16.4)
	AVG writes/VM      : 389.866666667 (std=7.0)
	AVG. Read Latency  : 3.9ms
	AVG. Write Latency : 19.0ms
	AVG. Latency       : 11.4ms

NB.
- Summary statistics are calculated from the data points in the final json file 
  (usually the run with the highest vm density)
- high std dev values indicate inconsistent performance across vm's

```

By default 'genchart' will launch a window showing you the graph.  
eg.

![example output](images/example.png)

### Script Options
The complete workflow revolves around just two scripts; `run-workload.sh` and `gencharts.py`. This section documents the options that may be used with these scripts.

```
run-workload.sh
---------------

Script to run a given fio workload against a number of 
clients running fio daemons

Options
        -j .... filename which contains the fio job parameters (REQUIRED)
        -t .... target volume name (REQUIRED)
        -f .... configuration file name (default is 'run-workload.yaml')
        -m .... mode to run, 'stepped' (default) or immediate. 
                - stepped ramps up the workload one client at a time
                - immediate starts the workload on all clients at once
        -s .... turn on gluster vol profile for the run (default is off)
        -d .... debug - do nothing except echo actions to the console
        -q .... override the qdepth in the job file for this run
        -r .... override the runtime defined (secs)
        -n .... override the number of fio processes/client for this run
        -h .... display help and exit
        -o .... output directory for fio json files etc
 
```  

The options available when generating the I/O summary chart are;
```markdown
[paul@work reporting]$ ./genchart.py -h
Usage: genchart.py [options]

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -D, --debug           turn on debug output
  -p FIO_FILE_PATH, --pathname=FIO_FILE_PATH
                        file name/path containing fio json output
  -t TITLE, --title=TITLE
                        Chart title
  -s SUBTITLE, --subtitle=SUBTITLE
                        Chart subtitle
  -o OUTPUT_FILE, --output=OUTPUT_FILE
                        output filename

```

### Example output during run-workload.sh  
```markdown
[root@work controller]# ./run-workload.sh -j randrw7030_test.job -r 60 -t ssd_data -o ~/output

20:39:41 Checking fio daemon is accessible on each client
- fio daemon on 'r73_01' is OK
- fio daemon on 'r73_02' is OK
- fio daemon on 'r73_03' is OK
- fio daemon on 'r73_04' is OK
- fio daemon on 'r73_05' is OK
- fio daemon on 'r73_06' is OK

Settings for this run;
  - configuration file used is 'run-workload.yaml'
  - 6 client(s) listed
  - 3 host(s) listed
  - gluster commands routed through gprfs029
  - fio jobfile called randrw7030_test.job
  - gluster volume 'ssd_data'
  - run mode is 'stepped'
  - output files will be written to '/root/output'
  - runtime override applied (changed to 60)
  - gluster stats NOT being captured for this run
20:39:48 getting vol info for ssd_data

20:39:54 Execution starting;
20:39:54 flushing page cache across each hypervisor
20:40:15 waiting 10 secs
20:40:25 running fio stream for 1 concurrent clients
20:41:27 output written to randrw7030_test.job_ssd_data_001_json.out] [eta 00m:00s]
20:41:27 flushing page cache across each hypervisor
20:41:50 waiting 10 secs
20:42:00 running fio stream for 2 concurrent clients
20:43:03 output written to randrw7030_test.job_ssd_data_002_json.outps] [eta 00m:00s]
20:43:03 flushing page cache across each hypervisor
20:43:24 waiting 10 secs
20:43:34 running fio stream for 3 concurrent clients
20:44:37 output written to randrw7030_test.job_ssd_data_003_json.outops] [eta 00m:00s]
20:44:37 flushing page cache across each hypervisor
20:45:00 waiting 10 secs
20:45:10 running fio stream for 4 concurrent clients
20:46:14 output written to randrw7030_test.job_ssd_data_004_json.outps] [eta 00m:00s]
20:46:14 flushing page cache across each hypervisor
20:46:36 waiting 10 secs
20:46:46 running fio stream for 5 concurrent clients
20:47:50 output written to randrw7030_test.job_ssd_data_005_json.outops] [eta 00m:00s]
20:47:50 flushing page cache across each hypervisor
20:48:11 waiting 10 secs
20:48:21 running fio stream for 6 concurrent clients
20:49:27 output written to randrw7030_test.job_ssd_data_006_json.outps] [eta 00m:00s]

removing temporary fio job file
moving output files to /root/output
20:49:27 Run sequence complete

```

Have fun testing!