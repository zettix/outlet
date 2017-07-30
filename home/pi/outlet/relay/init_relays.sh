#!/bin/bash
for i in `seq 0 7`; do
  /usr/local/bin/gpio mode $i out
done
oldstat="/home/pi/outlet/relay/oldstat"
val=255
if [ -f $oldstat ] ; then
  echo "Loading old statfile $oldstat"
  val=`cat $oldstat`
  echo "Read: $val"
fi
/usr/local/bin/gpio wb $val
