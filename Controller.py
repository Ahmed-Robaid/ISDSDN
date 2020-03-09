from pox.core import core
import pox.openflow.libopenflow_01 as of

from pox.lib.revent import *
from pox.lib.util import dpid_to_str
from pox.lib.util import str_to_bool
from pox.lib.util import dpidToStr
from pox.lib.addresses import EthAddr
from pox.lib.addresses import IPAddr
from pox.lib.packet import *
from pox.lib.packet.packet_base import packet_base
from types import *
import os
import csv
import time
import hashlib
import datetime

log = core.getLogger()

s1_dpid=0
s2_dpid=0
s3_dpid=0
s4_dpid=0
s5_dpid=0
serverIP = "10.0.10.10"
#number of illegal packets from the user to block him 
k=10
diff = 500

class MyHub (object):
	rulesCount = 0
   	def __init__ (self, connection):
		# Keep track of the connection to the switch so that we can
		# send it messages!
		self.connection = connection
		msg1=of.ofp_flow_mod()
		msg1.priority = 90
		# This binds our PacketIn event listener
		connection.addListeners(self)
		msg1.actions.append(of.ofp_action_output(port=of.OFPP_CONTROLLER))
		self.connection.send(msg1)
		self.dict = {}
		self.countList = {}
		self.cookies = 0
		self.fisrtTime = {}
		self.lastTime = {}

	def _handle_PacketIn (self, event):
		self.cookies = self.cookies + 1 
		# Handles packet in messages from the switch.
		packet = event.parsed # This is the parsed packet data.
		if not packet.parsed:
			log.warning("Ignoring incomplete packet")
	       		return

		statusDic = {}
		
		#print "packet arrived\n\n"
		srcMac = packet.src
		dstMac = packet.dst
		
		ip=packet.find('ipv4')		
		if ip is None:
			if packet.type == 0x0806 :#and not event.connection.dpid == s5_dpid: 
				log.debug("This packet is arp Packet")
				msg=of.ofp_flow_mod()
				msg.match.dl_type = 0x0806 #arp packet
				msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
				self.connection.send(msg)
			print "\n\n\nSent\n\n"
			return



		srcIP = ip.srcip
    		dstIP = ip.dstip
		
		if packet.find('tcp') is None:
			return
		else:
			segment = packet.find('tcp')
	

		srcPort = segment.srcport 
		dstPort = segment.dstport 
#		print MyHub.rulesCount 

#		print "----"
		data = str(srcMac) + "," + str(dstMac)#+ "," + str(srcPort)+ "," + str(dstPort)
		if segment.SYN and not segment.ACK :
			data = str(srcMac) + "," + str(dstMac)#+ "," + str(srcPort)+ "," + str(dstPort)
			x = 0		
			if srcMac in self.countList:
				c = self.countList[srcMac]
				c=c+1
				self.countList[srcMac]=c
				x=c				
			else:
				self.countList[srcMac]=1
				self.fisrtTime[srcMac] = int(round(time.time() * 1000))
				x=1
				self.dict[data] = "SYN"
				return
			
			if x >= k:
				msg=of.ofp_flow_mod()
				msg.match.dl_src = srcMac	
				self.connection.send(msg)
				#self.yazid(srcMac)
				if data in self.dict:				
					self.dict.pop(data)
				print "attack detected time from host %s"%srcMac
				print "detcetion time    : ",self.fisrtTime[srcMac] -int(round(time.time() * 1000)), "ms"
				MyHub.rulesCount = MyHub.rulesCount + 1
				return
			diffTime = (int(round(time.time() * 1000)) - self.fisrtTime[srcMac] )
			if diffTime  <= (2 ** (x -2)) + diff  or diffTime  >= (2 ** (x -2)) -diff: #was not found on the list				
				self.lastTime[srcMac] = int(round(time.time() * 1000))
				self.dict[data] = "SYN"
				msge=of.ofp_packet_out()
				msge.buffer_id = event.ofp.buffer_id
				msge.data = event.ofp.data
				msge.actions.append(of.ofp_action_output(port=1))
				self.connection.send(msge)	
				MyHub.rulesCount = MyHub.rulesCount + 1
#				print "first SYN"

		elif segment.RST and srcIP == serverIP:
			data = str(dstMac)  + "," +  str(srcMac)#+ "," + str(dstPort) + "," + str(srcPort)
			if dstMac in self.countList:
				c = self.countList[dstMac]
				c=c+1
				self.countList[dstMac]=c				
			else:
				self.countList[dstMac]=1
				
			if self.countList[dstMac] >= k:
				msg=of.ofp_flow_mod()
				msg.match.dl_src = dstMac	
				msg.actions.append()
				self.connection.send(msg)
				self.dict.pop(data)
				MyHub.rulesCount = MyHub.rulesCount + 1
				return
			self.dict[data] = "RST"
#			print " RST PACKET ! "


		elif segment.SYN and segment.ACK:
			data = str(dstMac)  + "," +  str(srcMac)#+ "," + str(dstPort) + "," + str(srcPort)
			self.dict[data] = "SYN-ACK"
			msge=of.ofp_packet_out()
			msge.buffer_id = event.ofp.buffer_id
			msge.data = event.ofp.data
			msge.actions.append(of.ofp_action_output(port=int(str(dstIP).split(".")[3])))
			self.connection.send(msge)
			msg=of.ofp_flow_mod()
			msg.idle_timeout = 3
			msg.cookie = self.cookies	
			msg.match.dl_dst = dstMac
			msg.match.dl_src = srcMac		
			msg.actions.append(of.ofp_action_output(port=int(str(dstIP).split(".")[3])))
			self.connection.send(msg)
			MyHub.rulesCount = MyHub.rulesCount + 1
			if srcMac in self.countList:
				count = self.countList.get(dstMac)
			else :
				count = 0
			self.countList[dstMac] = count + 1
#			print " SYN-ACK PACKET ! "

		elif segment.ACK:
			log.debug(" ACK PACKET ! ")
			if data not in self.dict :
				print "Ack without status record "
			elif self.dict.get(data) == "SYN-ACK":
				self.dict[data] = "ACK"
				msge=of.ofp_packet_out()
				msge.buffer_id = event.ofp.buffer_id
				msge.data = event.ofp.data
				msge.actions.append(of.ofp_action_output(port=1))
				self.connection.send(msge)
				msg=of.ofp_flow_mod()
				msg.cookie = self.cookies
				msg.match.dl_src = srcMac	
				msg.actions.append(of.ofp_action_output(port=1))
				self.connection.send(msg)
				MyHub.rulesCount = MyHub.rulesCount + 1
				msg=of.ofp_flow_mod()
				msg.match.dl_dst = srcMac
				msg.cookie = self.cookies	
				msg.actions.append(of.ofp_action_output(port=int(str(srcIP).split(".")[3])))
				self.connection.send(msg)
				MyHub.rulesCount = MyHub.rulesCount + 1
			else:
				msge=of.ofp_packet_out()
				msge.buffer_id = event.ofp.buffer_id
				msge.data = event.ofp.data
				msge.actions.append(of.ofp_action_output(port=1))
				self.connection.send(msge)
				
			if srcMac in self.countList:
				count = self.countList.get(srcMac)
			else :
				count = 0
			self.countList[srcMac] = count + 1


def launch ():
    # Starts the component
    def start_switch (event):
        log.debug("Controlling %s" % (event.connection,))
        MyHub(event.connection)
        
    core.openflow.addListenerByName("ConnectionUp", start_switch)

