#!/bin/bash

if [ $# -lt 1 ]; then
  echo "Usage: $0 /relay_number/-all"
  exit 1
fi
i=$1

if [ "X$i" == "X-all" ]; then
  for x in `seq 0 7` ; do
    echo "Tuning relay $x off."
    /usr/local/bin/gpio write $x 1
    sleep 1
  done
else
  if [ $i -lt 1 ] || [ $i -gt 8 ]; then
    echo "Relay must be between 1 and 8"
    exit 1
  fi
  echo "Tuning relay $i off."
  p=`expr $1 - 1`
  echo "actual pin: $p"
  /usr/local/bin/gpio write $p 1
fi
