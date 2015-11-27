# fio-tools
This project contains some tools to make performance reporting with fio a little easier when working with gluster and ovirt. The goal is to use fio to benchmark latencies within vm's and then use the fio results as input to a plot routing (matplotlib.pylot), to simplify interpretation of the results.  
  
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
  
###Testing  
1. The run-workload.sh script uses the 'job_sequence' file to run a given workload against  
2. Execution is cumulative through this job_sequence list  
3. The output is generated to files named 
```  
<fio_job_name><volume name><# vm's active>_json.out  
```  
e.g.  
randr100_100iops.job_sharded-512_001_json.out  
  
Here's an example execution  
```
[user@controller]#./run-workload.sh -j randrw8020_100iops.job -t sharded-512 -s  
```  

**TIP:** You can used -s on run-workload.sh to automatically gather gluster vol profile data  

###Generating Graphs  
1. Once the test run is complete, transfer the files over to your desktop where you have the reporting component.  
2. Place all the files in a single directory, and use the fio-collector module to produce the required chart  
e.g. 
``` 
[user@reporting]#./fio_collector.py -p 80-20-100iops -k 'mixed/clat/percentile/95.000000' -t "chart title" -o "output-file_name.png"  
```  
  
##Disclaimer  
This is the initial code commit with a new code directory layout. The code itself works but I haven't had the chance to confirm the instructions above with a clean environment.  
