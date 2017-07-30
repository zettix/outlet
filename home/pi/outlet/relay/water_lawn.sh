#!/bin/bash
# Sample script to have cron, a script, or a shell (suggest in screen)
#    control an outlet.
outlet=2
delay=3600 # 60 minutes
echo "Delay is $delay OK. $(date)"
# /usr/local/bin/gpio readall
/home/pi/outlet/relay/relay_on.sh $outlet
sleep $delay
/home/pi/outlet/relay/relay_off.sh $outlet
