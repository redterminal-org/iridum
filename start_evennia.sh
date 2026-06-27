#!/bin/bash
### Start Script for evennia.service ###

source ~/evennia/bin/activate
cd ~/iridum
evennia start
sleep 10
evennia reload

while true
do
  sleep 600
done

