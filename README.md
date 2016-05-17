# fio-tools
This project contains some tools to make measureing performance with fio a little easier when working with gluster and ovirt. The goal is to use fio to benchmark latencies within vm's and then use the fio results as input to a plot routing (matplotlib.pylot), to simplify interpretation of the results.  
  
##Workflow
###Pre-Requisites  
+ Use a node to act as the test manager/controller  
+ have passwordless ssh setup between your controller and the test vm's  
+ have passwordless ssh setup between your controller and the hypervisor nodes  
+ the code assumes that all test vm's are started 
+ for best results distribute the vm's across the hypervisors evenly
+ cp the controller directory to your controller node  
+ cp the reporting directory to your desktop, where you'll generate the charts from 
+ each test vm needs fio installed  
+ each test vm should have an instance of an fio daemon running  (fio --server --daemonize=/var/run/fio-svr.pid)  
  
  
###Script Options
The fio workload that is pushed to each of the clients can be 'tweaked' at run time, through several options available within the run-workload.sh script. 
Here are the options available

```
run-workload.sh
 
Script to run a given fio workload against a number of 
clients, typically fio daemons running in virtual machines

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
	-n .... override the number of fio processes/client for this run  
	-h .... display help and exit  
```  
  
##Running a Workload 
1. The run-workload.sh script uses a configuration file, which contains the gluster/ovirt nodes and the clients that will be running the fio jobs
2. There are two modes (-m) of execution   
2.1 'stepped' .... the fio workload is incremental, adding a client from the list at each iteration  
2.2 'immediate' .. the complete client list is run at once
3. The output is generated to files named 
```  
<fio_job_name><volume name><# vm's active>_json.out  
```  
e.g.  
randr100_100iops.job_sharded-512_001_json.out  
  
Here's an example run  
```
[root@gprfc088 perf_tests]# ./run-workload.sh -j randrw9010.job -t vmstore -m immediate  
  
Settings for this run;  
  - configuration file used is 'run-workload.yaml'  
  - 1 client(s) listed  
  - 3 host(s) listed  
  - gluster commands routed through gprfc085  
  - fio jobfile called randrw9010.job  
  - gluster volume 'vmstore'  
  - run mode is 'immediate'  
  - gluster stats NOT being captured for this run  
  
Execution starting;  
- flushing page cache across each hypervisor  
- waiting 10 secs  
- running fio stream for 1 concurrent clients  
- output written to randrw9010.job_vmstore_001_json.out  
  
removing temporary fio job file  
Run sequence complete  
```  

**TIP:** You can used -s on run-workload.sh to automatically gather gluster vol profile data  

###Generating Graphs  
1. Once the test run is complete, transfer the files over to your desktop where you have the reporting component.  
2. Place all the files in a single directory, and use the fio-collector module to produce the required chart  
e.g. 
``` 
[user@reporting]#./fio_collector.py -p 80-20-100iops -k 'mixed/clat/percentile/95.000000' -t "95%ile Latencies" -o "output-graph.png"  
```  
  
##Disclaimer  
This is the initial code commit with a new code directory layout. The code itself works but I haven't had the chance to confirm the instructions above with a clean environment.  
