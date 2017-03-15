#!/usr/bin/bash

# Assumptions for the run;
# 1) all vm's are started

# default filenames used by the script
CFG_FILE="run-workload.yaml"
FIO_TEMPFILE=$(mktemp)

FIO_PORT=8765
declare -a CLIENT
declare -a HOST

# run modes 
MODES[0]="stepped"
MODES[1]="immediate"

function usage {
  :
  echo -e "\nrun-workload.sh"
  echo -e "---------------\n"
  echo -e "Script to run a given fio workload against a number of"\
       "\nclients running fio daemons\n"
  echo "Options"
  echo -e "\t-j .... filename which contains the fio job parameters (REQUIRED)"
  echo -e "\t-t .... target volume name (REQUIRED)"
  echo -e "\t-f .... configuration file name (default is '${CFG_FILE}')"
  echo -e "\t-m .... mode to run, 'stepped' (default) or immediate. "
  echo -e "\t        - stepped ramps up the workload one client at a time"
  echo -e "\t        - immediate starts the workload on all clients at once"
  echo -e "\t-s .... turn on gluster vol profile for the run (default is off)"
  echo -e "\t-d .... debug - do nothing except echo actions to the console"
  echo -e "\t-q .... override the qdepth in the job file for this run"
  echo -e "\t-r .... override the runtime defined (secs)"
  echo -e "\t-n .... override the number of fio processes/client for this run"
  echo -e "\t-h .... display help and exit"
  echo -e "\t-o .... output directory for fio json files etc\n"
  
}

function timestamp {
  now=$(date +%H:%M:%S)
  echo $now
  }

function fio_OK {
  # 0 .. OK
  # 1 .. Not OK
  local rc=0
  local client
  local port_open=0

  echo -e "\n$(timestamp) Checking fio daemon is accessible on each client"

  # Process the client list, and check FIO_PORT is open on each one
  for client in "${CLIENT[@]}"; do
    port_open=$(nc $client $FIO_PORT < /dev/null &> /dev/null; echo $?)
    if [ $port_open -gt 0 ]; then 
      echo "- fio daemon on '${client}' is not accessible"
      rc=1
    else
      echo "- fio daemon on '${client}' is OK"
    fi

  done
  
  return $rc
}

function drop_page_cache {
  :
  local delay_secs=10
  echo "$(timestamp) flushing page cache across each hypervisor"
  for host in "${HOST[@]}"; do 
    $CMD_PFX ssh -n $host 'echo 3 > /proc/sys/vm/drop_caches && sync'
  done

  echo "$(timestamp) waiting ${delay_secs} secs"
  $CMD_PFX sleep ${delay_secs}
}

function get_vol_profile {
  local profile_output=vol_profile_${TARGET}_${1}_${2}
  echo "- writing volume profile data to $profile_output"
  $CMD_PFX ssh -n ${HOST[0]} "gluster vol profile $TARGET info " > $profile_output
}

function get_vol_info {
  local vol_info_file=${OUTDIR}/vol-info-${TARGET}
  echo "$(timestamp) getting vol info for ${TARGET}"
  $CMD_PFX ssh -n ${HOST[0]} "gluster vol info $TARGET" > $vol_info_file
}

function run_fio {
  local -a vm_names=("${!1}")
  local num_vms=${#vm_names[@]}
  local num_vms_fmtd=$(printf "%03d" $num_vms)
  local output_file=${OUTDIR}/${JOBNAME}_${TARGET}_${num_vms_fmtd}_json.out
  local client_string=""
  
  for vm in "${vm_names[@]}"; do
    client_string="$client_string --client=${vm}"
  done
 
  echo "$(timestamp) running fio stream for ${num_vms} concurrent clients"
  $CMD_PFX fio ${client_string} --output=${output_file} --output-format=json $FIO_TEMPFILE
  echo "$(timestamp) output written to ${output_file}"
  
  if [ "$GETSTATS" ]; then
    :
    get_vol_profile $num_vms_fmtd $JOBNAME
    vol_profile clear
  fi
}

function vol_profile {
  local desired_state=$1
  case $desired_state in
    on)
       echo "  - gluster profile stats enabled for '${TARGET}'"
       $CMD_PFX ssh -n ${HOST[0]} "gluster vol profile $TARGET start"
       $CMD_PFX ssh -n ${HOST[0]} "gluster vol profile $TARGET info clear"
       ;;
    off)
       echo "  - gluster profile stats disabled for '${TARGET}'"
       $CMD_PFX ssh -n ${HOST[0]} "gluster vol profile $TARGET stop"
       ;;
    clear)
       echo "  - gluster profile stats cleared for '${TARGET}'"
       $CMD_PFX ssh -n ${HOST[0]} "gluster vol profile $TARGET info clear"
       ;;
  esac
}

function process_clients {
  
  echo -e "\n$(timestamp) Execution starting;"
  local client
  
  case $FIO_CLIENT_MODE in 
    stepped)
       declare -a client_list
       for client in ${CLIENT[@]}; do 
         client_list+=($client)
         drop_page_cache
         run_fio client_list[@] 
       done
       ;;
    immediate)
       drop_page_cache
       run_fio CLIENT[@]
       ;;
  esac

}

function build_clients {
  :	
  read -a CLIENT <<< $(cat $CFG_FILE | python -c "import yaml,sys; cfg=yaml.load(sys.stdin); print ' '.join(cfg['clients'])")
}

function build_hosts {
  :  
  read -a HOST <<< $(cat $CFG_FILE | python -c "import yaml,sys; cfg=yaml.load(sys.stdin); print ' '.join(cfg['hosts'])")
}


function update_fio_job {
  # passed variable to update, and the value

  case "$1" in
    iodepth|numjobs|runtime)
            if grep -q ${1} "$FIO_TEMPFILE" ; then
              sed -i "s/${1}=.*/${1}=${2}/" $FIO_TEMPFILE
              echo "  - ${1} override applied (changed to ${2})"
            fi
            ;;
    *)
        echo "Unknown update option for fio job file"
        exit 16
        ;;
  esac

}



function main {
  :
  # build list of the hosts in the cluster from control file
  build_hosts

  # populate the CLIENTS array from the 'job_sequence' file
  build_clients 

  # fio daemon on every client specified MUST be accessible - if not abort
  if ! fio_OK ; then 
    echo -e "Run aborted, unable to continue.\n"
    exit 16
  fi

  cp -f ${JOBNAME} ${FIO_TEMPFILE}


  echo -e "\nSettings for this run;"
  echo "  - configuration file used is '${CFG_FILE}'"
  echo "  - ${#CLIENT[@]} client(s) listed"
  echo "  - ${#HOST[@]} host(s) listed"
  echo "  - gluster commands routed through ${HOST[0]}"
  echo "  - fio jobfile called ${JOBNAME}"
  echo "  - gluster volume '${TARGET}'"
  echo "  - run mode is '${FIO_CLIENT_MODE}'"
  echo "  - output files will be written to '${OUTDIR}'"

  if [ "${QDEPTH}" ]; then 
    update_fio_job 'iodepth' ${QDEPTH}
  fi
  if [ "${NUMJOBS}" ]; then 
    update_fio_job 'numjobs' ${NUMJOBS}
  fi
  if [ "${RUNTIME}" ]; then 
    update_fio_job 'runtime' ${RUNTIME}
  fi

  cp -f ${FIO_TEMPFILE} ${OUTDIR}/fio.job

  if [ "$GETSTATS" ]; then
    vol_profile on
  else
    echo "  - gluster stats NOT being captured for this run"
  fi

  get_vol_info
  process_clients

  echo -e "\nremoving temporary fio job file"
  rm -f $FIO_TEMPFILE
  
  echo "$(timestamp) Run sequence complete"  
  if [ "$GETSTATS" ]; then 
    vol_profile off
  fi

}



while getopts ":j:dst:m:f:q:n:r:o:h" opt; do

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
       CFG_FILE=$OPTARG
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
    q)
       QDEPTH=$OPTARG
       ;;
    r)
       RUNTIME=$OPTARG
       ;;
    n)
       NUMJOBS=$OPTARG
       ;;
    o)
       OUTDIR=$OPTARG
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

if ! [ -e "$CFG_FILE" ]; then 
  echo "-> Error, config filename provided not found (specify full path?)"
  exit 16
fi

if [ -z "${OUTDIR}" ]; then

  OUTDIR=$(pwd)/output
  echo "-> using default output directory of '${OUTDIR}'"

  if ! [ -d "$OUTDIR" ]; then
    echo "   - creating new dir '${OUTDIR}'"
    mkdir ${OUTDIR}
  fi
else
  if ! [ -d "$OUTDIR" ]; then
    echo "-> Error, output directory must exist prior to the run"
    exit 16
  fi
fi

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

