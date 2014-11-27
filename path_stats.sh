#!/bin/bash

######################################################
# path_stats.sh - for a given set of hosts, run an mtr 
#    and output the complete path on a single line in 
#    the format date::ip_hop(latency,loss)->
#    and put the entries into a logfile $OUTPUT/<hostname>.log
#    20141126 - first rev
#######################################################

PATH=${PATH}:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

## We want to run MTR in report mode, force IPv4, run 10 cycles and have 5 second pause between cycles to attempt to minmise ICMP rate limiting giving false positives for loss
MTR_BIN=`which mtr`
MTR_OPS=" -4 -n -r -c 10 -i 5 "

DATE_BIN=`which date`
GREP_BIN=`which grep`
AWK_BIN=`which awk`
OUTPUT_DIR="/tmp"


## List of "ping hosts", can be space or newline seperated. 
ping_host="<list of hosts here>"

for host in ${ping_host} 
do
	START=`${DATE_BIN}` && OUTPUT=`${MTR_BIN} ${MTR_OPS} ${host} | grep -vE '[A-Za-z]' | awk '{print $2, $3, $6}' | sed -e 's/\ /\(/g;s/\%/\)/g;s/)(/,/g' | tr "\n" "-" | sed -e 's/-/)->/g' | sed -e 's/->$//g'`  && echo "${START}::${OUTPUT}"  >> ${OUTPUT_DIR}/${host}.log  & 
	sleep 10
done 
