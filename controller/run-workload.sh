#!/usr/bin/bash

# assume for now that the fio daemon processes are active
# on each vm
# all vm's are started

# default filename containing the clients for the fio run
FILENAME="job_sequence"

FIO_PORT=8765
declare -a CLIENT

# run modes 
MODES[0]="stepped"
MODES[1]="immediate"

function usage {
  :
  echo -e "\nrun-workload.sh"
  echo -e "---------------\n"
  echo -e "Script to run a given fio workload against a number of"\
       "\nclients, typically fio daemons running in virtual machines\n"
  echo "Options"
  echo -e "\t-j .... filename which contains the fio job parameters (REQUIRED)"
  echo -e "\t-t .... target volume name (REQUIRED)"
  echo -e "\t-f .... filename which contains a row for each fio client"
  echo -e "\t        (default = job_sequence)"
  echo -e "\t-m .... mode to run, 'stepped' (default) or immediate. "
  echo -e "\t        - stepped ramps up the workload one client at a time"
  echo -e "\t        - immediate starts the workload on all clients at once"
  echo -e "\t-s .... turn on gluster vol profile for the run (default is off)"
  echo -e "\t-d .... debug - do nothing except echo actions to the console"
  echo -e "\t-h .... display help and exit\n"     
  
}

function fio_OK {
  # 0 .. OK
  # 1 .. Not OK
  local rc=0
  local client
  local port_open=0
  
  # Process the client list, and check FIO_PORT is open on each one
  for client in "${CLIENT[@]}"; do
    port_open=$(nc $client $FIO_PORT < /dev/null &> /dev/null; echo $?)
    if [ $port_open -gt 0 ]; then 
      echo "-> Error, fio daemon on '${client}' is not accessible"
      rc=1
    fi
  done
  
  return $rc
}

function drop_cache {
  :
  local delay_secs=10
  echo "- flushing page cache across each hypervisor"
  $CMD_PFX ssh -n gprfc085 'echo 3 > /proc/sys/vm/drop_caches && sync'
  $CMD_PFX ssh -n gprfc086 'echo 3 > /proc/sys/vm/drop_caches && sync'
  $CMD_PFX ssh -n gprfc087 'echo 3 > /proc/sys/vm/drop_caches && sync'
  echo "- waiting ${delay_secs} secs"
  $CMD_PFX sleep ${delay_secs}
}

function get_vol_profile {
  local profile_output=vol_profile_${TARGET}_${2}
  echo "- writing volume profile data to $profile_output"
  $CMD_PFX ssh -n gprfc085 "gluster vol profile $TARGET info " > $profile_output
}


function run_fio {
  local -a vm_names=("${!1}")
  local num_vms=${#vm_names[@]}
  local num_vms_fmtd=$(printf "%03d" $num_vms)
  local output_file=${JOBNAME}_${TARGET}_${num_vms_fmtd}_json.out
  local client_string=""
  
  for vm in "${vm_names[@]}"; do
    client_string="$client_string --client=${vm}"
  done
 
  echo "- running fio stream for ${num_vms} concurrent vm's"
  $CMD_PFX fio ${client_string} --output=${output_file} --output-format=json $JOBNAME
  echo "- output written to ${output_file}"
  
  if [ "$GETSTATS" ]; then
    :
    get_vol_profile $num_vms_fmtd $JOBNAME
  fi
}

function vol_profile {
  local desired_state=$1
  case $desired_state in
    on)
       echo "  - gluster profile stats enabled for '${TARGET}'"
       $CMD_PFX ssh -n gprfc085 "gluster vol profile $TARGET start"
       ;;
    off)
       echo "  - gluster profile stats disabled for '${TARGET}'"
       $CMD_PFX ssh -n gprfc085 "gluster vol profile $TARGET stop clear"
       ;;
  esac
}

function process_clients {
  
  echo -e "\nExecution starting;"
  local client
  
  case $FIO_CLIENT_MODE in 
    stepped)
       declare -a client_list
       for client in ${CLIENT[@]}; do 
         client_list+=($client)
         drop_cache
         run_fio client_list[@] 
       done
       ;;
    immediate)
       drop_cache
       run_fio CLIENT[@]
       ;;
  esac

}

function build_clients {
  :	
  while read -r vm_name; do

    if [[ ! $vm_name =~ ^# ]]; then
      CLIENT+=($vm_name)
    fi
  done < ${FILENAME}
}


function main {
  :

  # populate the CLIENTS array from the 'job_sequence' file
  build_clients 
  
  if ! fio_OK ; then 
    echo -e "Run aborted, unable to continue.\n"
    #exit 16
  fi

  echo -e "\nSettings for this run;"
  echo "  - file containing the fio client list is '${FILENAME}'"
  echo "  - ${#CLIENT[@]} client(s) listed"
  echo "  - fio jobfile called ${JOBNAME}"
  echo "  - vm's are on gluster volume '${TARGET}'"
  echo "  - run mode is '${FIO_CLIENT_MODE}'"

  if [ "$GETSTATS" ]; then 
    vol_profile on
  else
    echo "  - gluster stats NOT being captured for this run"
  fi  
  
  process_clients
  
  echo -e "\nRun sequence complete"  
  if [ "$GETSTATS" ]; then 
    vol_profile off
  fi
}



while getopts ":j:dst:m:f:h" opt; do 
  case $opt in 
    j)
       JOBNAME=$OPTARG
       ;;
    s)
       GETSTATS=true
       ;;
    h) 
       usage
       exit 0
       ;;
    f)
       FILENAME=$OPTARG
       if ! [ -e "$FILENAME" ]; then 
         echo "-> Error, filename provided not found (specify full path?)"
         exit 16
       fi
       ;;
    m)
       FIO_CLIENT_MODE=$OPTARG
       # confirm the mode is valid
       if ! [[ ${MODES[@]} =~ "$FIO_CLIENT_MODE" ]]; then
         echo "-> Error, invalid run mode (-m), choose one of the following: ${MODES[@]}"
         exit 16
       fi
	   ;;
    t)
       TARGET=$OPTARG
       ;;
    d)
       DEBUG=true 
       ;;
    \?)
       echo "Invalid option"
       exit 16
       ;;
  esac

done

if [ -z "${JOBNAME}" ] || [ -z "${TARGET}" ]; then
  echo "job name and target volume must be supplied"
  exit 12
else 
  if [ ! -e "$JOBNAME" ]; then 
    echo "Job name given but file does not exist"
    exit 12
  fi
fi

if [ -z "${FIO_CLIENT_MODE}" ]; then 
  FIO_CLIENT_MODE=${MODES[0]}
fi


if [ "$DEBUG" ]; then 
  CMD_PFX="echo DEBUG -->"
else
  CMD_PFX=""
fi 

main 

