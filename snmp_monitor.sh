#!/bin/sh
cd /home/pi/snmp_monitor/
python snmp_monitor.py 2>&1 > /dev/null
