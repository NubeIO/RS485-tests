#! /bin/bash
# Running on ci534 ./testmodbus.sh /dev/

declare -A results=()
GLOBAL_ERROR_STATE=0
GLOBAL_TEMP_ERROR=0
READ_TIMEOUT=10
WRITE_TIMEOUT=10

ARCH=$(dpkg --print-architecture)
if [ "$ARCH" = "amd64" ]; then
    ARCH_PATH="x86_64-linux-gnu"
elif [ "$ARCH" = "aarch64" ]; then
    ARCH_PATH="aarch64-linux-gnu"
elif [ "$ARCH" = "armhf" ]; then
    ARCH_PATH="arm-linux-gnueabihf"
else
    PARCH_PATHATH="i686-linux-gnu"
fi


# $1 output
# $2 register
# $3 expected value
check_val() {
    val=$(echo "${1}" | grep "\[$2\]" | cut -d ' ' -f 2)
    if [ ! -z "$val" ] && [ $val == "$3" ]; then
        echo -e "\t\tRegister $2 correct" 1>&2
        return 0
    fi
    echo -ne "Expected register $2 to be $3 got $val for " 1>&2
    GLOBAL_ERROR_STATE=1
    GLOBAL_TEMP_ERROR=$((GLOBAL_TEMP_ERROR + 1))
    return 1
}

error() {
    echo "/////////////////////////////////////////////////////////////////////"
    echo "$1"
    echo "/////////////////////////////////////////////////////////////////////"
    GLOBAL_ERROR_STATE=1
}


# Run a Modbus test between a master and a slave device.
# Arguments:
#   $1: Master port
#   $2: Slave port
#   $3: Baud rate
run_test() {
  local master_port=$1
  local slave_port=$2
  local baud_rate=$3
  local slave_pid
  local output
  local ret

  echo "Testing master@${master_port}  slave@${slave_port} with baud ${baud_rate}"
  GLOBAL_TEMP_ERROR=0

  # Start the slave in the background
  ./diagslave/"${ARCH_PATH}"/diagslave -b "${baud_rate}" -p none -m rtu -a 3 "${slave_port}" >/dev/null &
  slave_pid=$!
  sleep 1

  # Check if slave started successfully
  if ! ps -p "${slave_pid}" >/dev/null; then
    echo "Slave failed to start. Skipping" >&2
    GLOBAL_TEMP_ERROR=-1000
    results["${baud_rate}"]=${GLOBAL_TEMP_ERROR}
    return
  fi

  # Test initial reads
  echo -e "\tTesting initial reads" >&2
  if ! output=$(./modpoll/"${ARCH_PATH}"/modpoll -b "${baud_rate}" -o "${READ_TIMEOUT}" -1 -p none -m rtu -a 3 -r 500 -c 10 "${master_port}" 2>/dev/null); then
    echo "POLLING FAILED" >&2
    GLOBAL_TEMP_ERROR=-2000
  else
    for register in {500..509}; do
      check_val "${output[@]}" $((register)) 0 || echo "master@${master_port} slave@${slave_port} with baud ${baud_rate}" >&2
    done

    # Test write of values
    echo -e "\tTesting write of values" >&2
    if ! ./modpoll/"${ARCH_PATH}"/modpoll -b "${baud_rate}" -o "${WRITE_TIMEOUT}" -p none -m rtu -a 3 -r 500 -c 10 "${master_port}" 1 2 3 4 5 6 7 8 9 10 >/dev/null; then
      echo "Write Failed" >&2
      GLOBAL_TEMP_ERROR=-3000
    else
      # Test updated reads
      echo -e "\tTesting updated reads" >&2
      if ! output=$(./modpoll/"${ARCH_PATH}"/modpoll -b "${baud_rate}" -o "${READ_TIMEOUT}" -1 -p none -m rtu -a 3 -r 500 -c 10 "${master_port}" 2>/dev/null); then
        echo "Polling failed on update" >&2
        GLOBAL_TEMP_ERROR=-4000
      else
        for register in {500..509}; do
          check_val "${output[@]}" $((register)) $((register - 499)) || echo "master@${master_port} slave@${slave_port} with baud ${baud_rate}" >&2
        done
      fi
    fi
  fi

  results["${baud_rate}"]=${GLOBAL_TEMP_ERROR}
  kill "${slave_pid}"
}

#cleanup_slaves()
if [ $# -ne 2 ]; then
    echo "USAGE:"
    echo -e "\t $0 [port1] [port2]"
    echo -e "\t e.g. $0 /dev/ttyO4 /dev/tty05 on the ci534 or $0 /dev/ttyUSB0 /dev/ttyAMA0 on the edgeX1"
else

    run_test $2 $1 9600
    run_test $2 $1 19200
    run_test $2 $1 38400
    run_test $2 $1 57600
    run_test $2 $1 115200
    run_test $2 $1 230400
    run_test $2 $1 460800


    echo -e "\nRESULTS $1 -> $2 "
    echo "----------------------------------"
    for i in "${!results[@]}"; do
        if [ ${results[$i]} -eq 0 ]; then
            r="PASSED"
        else
            r="FAILED ${results[$i]} times"
        fi
        echo -e "${i}:\t$r"
    done
    declare -A results=()

    run_test $2 $1 9600
    run_test $2 $1 19200
    run_test $2 $1 38400
    run_test $2 $1 57600
    run_test $2 $1 115200
    run_test $2 $1 230400
    run_test $2 $1 460800

    echo -e "\nRESULTS $2 -> $1 "
    echo "----------------------------------"
    for i in "${!results[@]}"; do
        if [ ${results[$i]} -eq 0 ]; then
            r="PASSED"
        else
            r="FAILED ${results[$i]} times"
        fi
        echo -e "${i}:\t$r"
    done

    if [ $GLOBAL_ERROR_STATE -ne 0 ]; then
        error "AN ERROR OCCURED CHECK THE LOGS"
    else
        echo "Modbus works both ways at 9600 14400 19200 28800. 38400 57600 and 76800 baud"
    fi
fi
