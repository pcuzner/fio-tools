#!/usr/bin/bash

# assume for now that the fio daemon processes are active
# on each vm
# all vm's are started

function drop_cache {
  :
  local delay_secs=5
  echo "- dropping cache across each hypervisor"
  $CMD_PFX ssh -n gprfc085 'echo 3 > /proc/sys/vm/drop_caches'
  $CMD_PFX ssh -n gprfc086 'echo 3 > /proc/sys/vm/drop_caches'
  $CMD_PFX ssh -n gprfc087 'echo 3 > /proc/sys/vm/drop_caches'
  echo "- waiting ${delay_secs} secs"
  $CMD_PFX sleep ${delay_secs}
}

function get_vol_profile {
  local profile_output=vol_profile_${target_volume}_${1}_${2}
  echo "- writing volume profile data to $profile_output"
  $CMD_PFX ssh -n gprfc085 "gluster vol profile $target_volume info " > $profile_output
}


function run_fio {
  local -a vm_names=("${!1}")
  local num_vms=${#vm_names[@]}
  local num_vms_fmtd=$(printf "%03d" $num_vms)
  local job_name=$2
  local target=$3
  local output_file=${jobname}_${target}_${num_vms_fmtd}_json.out
  local client_string=""
  
  for vm in "${vm_names[@]}"; do
    client_string="$client_string --client=${vm}"
  done
 
  echo "- running fio stream for ${num_vms} concurrent vm's"
  $CMD_PFX fio ${client_string} --output=${output_file} --output-format=json $jobname
  echo "- output written to ${output_file}"
  
  if [ "$GETSTATS" ]; then
    :
    get_vol_profile $num_vms_fmtd $jobname
  fi
}

function vol_profile {
  local desired_state=$1
  case $desired_state in
    on)
       echo "  - turning gluster profile stats on"
       $CMD_PFX ssh -n gprfc085 "gluster vol profile $target_volume start"
       ;;
    off)
       echo "  - turning gluster profile stats off"
       $CMD_PFX ssh -n gprfc085 "gluster vol profile $target_volume stop clear"
       ;;
  esac
}


function main {
  local job_name=$1
  local target=$2
  :
  echo "Run will use;"
  echo "  - fio jobfile called ${jobname}"
  echo "  - vm's are on gluster volume ${target}"

  if [ "$GETSTATS" ]; then 
    vol_profile on
  else
    echo "  - gluster stats NOT being captured for this run"
  fi  


  declare -a client_list
  while read -r vm_name; do

    if [[ ! $vm_name =~ ^# ]]; then
      client_list+=($vm_name)
      drop_cache
      run_fio client_list[@] $job_name $target

    fi
  done < job_sequence

  echo -e "\nRun sequence complete"  
  if [ "$GETSTATS" ]; then 
    vol_profile off
  fi
}


while getopts ":j:dst:" opt; do 
  case $opt in 
    j)
       jobname=$OPTARG
       ;;
    s)
       GETSTATS=true
       ;;
    t)
       target_volume=$OPTARG
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

if [ -z "${jobname}" ] || [ -z "${target_volume}" ]; then
  echo "job name and target volume must be supplied"
  exit 12
else 
  if [ ! -e "$jobname" ]; then 
    echo "Job name given but file does not exist"
    exit 12
  fi
fi

if [ "$DEBUG" ]; then 
  CMD_PFX="echo DEBUG -->"
else
  CMD_PFX=""
fi 

main $jobname $target_volume

