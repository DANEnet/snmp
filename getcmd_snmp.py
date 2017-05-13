"""
Starting with 
http://pysnmp.sourceforge.net/docs/pysnmp-hlapi-tutorial.html


pysnmp.smi.error.SmiError: Excessive instance identifier sub-OIDs left at 
MibTableRow((1, 3, 6, 1, 2, 1, 2, 2, 1), None): (0,)


Alerts:
  no input (-50) for 5 minutes
 temperatureFlag,
 reflectedLevel >2 ,
                        rightlevel,
                        leftlevel,
frequency,
                        voltage (48 +- 1 v. ),
                        temperature (limit 90),
email eas --
login to automation from home. 
Streaming - 

"""
from pysnmp.hlapi import *
ifrom . import get_config

import re

def extract_integer(string_in):
  r = re.search(r"(?isux)Integer32\((\d+)\)", str(string_in))
  out_integer = int(r.group(1))
  return(out_integer)

def extract_text(string_in):
  rb = re.search(r"(?ismux)Integer32\(\'(\w+)\'", str(string_in))
  return(r.group(1))


def check_silence():
  g = getCmd(SnmpEngine(),
    CommunityData('public'),
    UdpTransportTarget(('192.168.0.22', 161)),
    ContextData(),
    ObjectType(ObjectIdentity('Technalogix', measure, 0))
    )
  data_string = next(g)
  

def get_readings():

  for measure in ("aGCSetPoint",
      "aGCSetPoint",
      "forwardlevel",
      "forwardlevel",
      "leftlevel",
      "reflectedLevel",
      "rightlevel",
      "temperature",
      "voltage",
      "vSWRTripPointDec"
      ):
    g = getCmd(SnmpEngine(),
      CommunityData('public'),
      UdpTransportTarget(('192.168.0.22', 161)),
      ContextData(),
      ObjectType(ObjectIdentity('Technalogix', measure, 0))
      )
    res_str = next(g)
    print((measure, res_str))
    res_int = extract_integer(str(res_str))
    print(measure, res_int)


  for measure in (
      "temperatureFlag",
      "overDrive",
      "vSWRFlag",
      ):
    g = getCmd(SnmpEngine(),
      CommunityData('public'),
      UdpTransportTarget(('192.168.0.22', 161)),
      ContextData(),
      ObjectType(ObjectIdentity('Technalogix', measure, 0))
      )
    res_str = next(g)
    print((measure, res_str))
    res_str2 = extract_text(str(res_str))
    print((measure, res_str2))





#x=ObjectIdentity('SNMPv2-MIB', 'system')
#print(tuple(x))

if __name__ == "__main__":
    get_readings()

