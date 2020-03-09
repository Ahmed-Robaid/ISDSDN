import threading
import sys
import random
import socket                                         
import time
import logging 
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *
import argparse
import os
import urllib2
count = 10000
ip = "10.0.10.10"
port= 80
iterationCount =0 
second = 0
reqPerSec = 3
#def worker(mac):

count = 10000
ip = "10.0.10.10"
port= 80
iterationCount =0 
second = 0
reqPerSec = 3
mac="00:00:00:00:00:01"
file1 = open(sys.argv[1], 'r')
lines = file1.readlines()
for line in lines:
	x = line.split(",")
	x[11] = x[11].replace('"','').strip()
	if str(x[11]) != "TCP":
		continue 
	s_IP = x[3]
        s_port = x[5].replace('"','').strip()
        d_port = x[6].replace('"','').strip()
	payload = int(x[10].replace('"','').strip()) * "a"
	a= Ether(dst=mac)/IP(dst=ip)/TCP(flags="S",  sport=int(s_port),  dport=int(port))/payload
	sendp(a)
	iterationCount = iterationCount + 1
	print(str(iterationCount) + " Packet Sent")

#while iterationCount < int(count):
#	for i in range(0,reqPerSec):
#	#	print time.time()
#		a= Ether(dst=mac)/IP(dst=ip)/TCP(flags="S",  sport=RandShort(),  dport=int(port))	
#		sendp(a,  verbose=0)
#		iterationCount = iterationCount + 1
#		print(str(iterationCount) + " Packet Sent")
#	time.sleep(1) 
