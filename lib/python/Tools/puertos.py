#!/usr/bin/python
import socket
import subprocess
import sys
from datetime import datetime

#clears the shell screen
subprocess.call('clear', shell=True)

#ask for input
remoteServer = "127.0.0.1"
remoteServerIP = socket.gethostbyname(remoteServer)

#print a banner saying we are scanning
print "----------------------------------------------------"
print "now scanning your host...", remoteServerIP
print "----------------------------------------------------"

#Check what time the scan started
t1 = datetime.now()

# Using the range function to specify which ports (1 - 1025)

#Errors.

try:
  for port in range(1, 65500):
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    result = sock.connect_ex((remoteServerIP, port))
    if result == 0:
        #if the socket is listening it will print out the port
      print("Port{}:\t Open".format(port))
    sock.close()

except socket.gaierror:
  print 'Hostname could not be resolved to IP. Exiting'
  sys.exit()

except socket.error:
  print "couldn't connect to server"
  sys.exit()

# checking the time again
t2 = datetime.now()

#calculates the differnce of time, to see how long it took to run the script
total = t2 - t1

#printing the info to screen
print "scanning compelte in :", total
