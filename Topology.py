#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import RemoteController
from mininet.cli import CLI
import time

totalNumOfUsers = 40
numOfUsers = int(totalNumOfUsers/4)
moreUser = 0
if totalNumOfUsers/float(4) > totalNumOfUsers/4 :
	moreUser = 1
c=RemoteController( "c0", ip='127.0.0.1' ,port=6633)

class SingleSwitchTopo( Topo ):
    "Single switch connected to n hosts."
    def build( self, n=1):
	switch1 = self.addSwitch( 's1' )
        switch2 = self.addSwitch( 's2' )
        switch3 = self.addSwitch( 's3' )
        switch4 = self.addSwitch( 's4' )
	switch5 = self.addSwitch( 's5' )
	switch6 = self.addSwitch( 's6' )
	serverSwitch = self.addSwitch( 's7' )

	link1G=dict(bw=1000)
	link100M=dict(bw=100)
        server = self.addHost( 'server' , ip='10.0.10.10/16' , mac='00:00:00:00:00:01')
	
        # Add links
        self.addLink( serverSwitch, server, **link1G )#g

	self.addLink( switch5, serverSwitch, **link1G) #e	
	self.addLink( switch1, switch5, **link1G) #a
	self.addLink( switch2, switch5, **link1G) #b

	self.addLink( switch6, serverSwitch, **link1G) #f
	self.addLink( switch3, switch6, **link1G) #c
	self.addLink( switch4, switch6, **link1G) #d
        
	self.addLink( switch5, switch6, **link1G) #h
	hosts =[]
	for i in range(0,numOfUsers+moreUser):
		host = self.addHost( 'Net1_h%s'%(i+2) , ip='10.0.1.%s/16'%(i+2) )
		self.addLink( host, switch1, **link100M ) #m
		hosts.append(host)

	for i in range(0,numOfUsers+moreUser):
		host = self.addHost( 'Net2_h%s'%(i+2) , ip='10.0.2.%s/16'%(i+2) )
		self.addLink( host, switch2, **link100M ) #m
		hosts.append(host)
	for i in range(0,numOfUsers):
		host = self.addHost( 'Net3_h%s'%(i+2) , ip='10.0.3.%s/16'%(i+2) )
		self.addLink( host, switch3, **link100M ) #m
		hosts.append(host)
	for i in range(0,numOfUsers):
		host = self.addHost( 'Net4_h%s'%(i+2) , ip='10.0.4.%s/16'%(i+2) )
		self.addLink( host, switch4, **link100M ) #m
		hosts.append(host)
	host = self.addHost( 'lg1', ip='10.0.1.'+str(numOfUsers +moreUser + 2)+'/16')
	self.addLink( host, switch1, **link100M ) #m
	host = self.addHost( 'lg2', ip='10.0.3.'+str(numOfUsers +moreUser+2)+'/16')
	self.addLink( host, switch3, **link100M )

def perfTest():
    "Create network and run simple performance test"
    topo = SingleSwitchTopo()
    net = Mininet( topo=topo,controller=RemoteController, link=TCLink )
    
    server = net.get('server')
    server.cmd('sudo python ~/web_server.py & ') 

    net.start()
    c.start()
    serverSwitch = net.get('s7')
    serverSwitch.cmd('sudo ovs-ofctl add-flow s7 cookie=0x1,dl_type=0x0800,nw_proto=6,nw_dst=10.0.10.10,actions=output:1')
    serverSwitch.cmd('sudo ovs-ofctl add-flow s7 cookie=0x1,dl_type=0x0800,nw_proto=6,nw_dst=10.0.1.0/24,actions=output:2')
    serverSwitch.cmd('sudo ovs-ofctl add-flow s7 cookie=0x1,dl_type=0x0800,nw_proto=6,nw_dst=10.0.2.0/24,actions=output:2')
    serverSwitch.cmd('sudo ovs-ofctl add-flow s7 cookie=0x1,dl_type=0x0800,nw_proto=6,nw_dst=10.0.3.0/24,actions=output:3')
    serverSwitch.cmd('sudo ovs-ofctl add-flow s7 cookie=0x1,dl_type=0x0800,nw_proto=6,nw_dst=10.0.4.0/24,actions=output:3')

    switch5 = net.get('s5')
    switch5.cmd('sudo ovs-ofctl add-flow s5 cookie=0x1,dl_type=0x0800,nw_proto=6,nw_dst=10.0.10.10,actions=output:1')
    switch5.cmd('sudo ovs-ofctl add-flow s5 cookie=0x1,dl_type=0x0800,nw_proto=6,nw_dst=10.0.1.0/24,actions=output:2')
    switch5.cmd('sudo ovs-ofctl add-flow s5 cookie=0x1,dl_type=0x0800,nw_proto=6,nw_dst=10.0.2.0/24,actions=output:3')
    switch5.cmd('sudo ovs-ofctl add-flow s5 cookie=0x1,dl_type=0x0800,nw_proto=6,nw_dst=10.0.3.0/24,actions=output:4')
    switch5.cmd('sudo ovs-ofctl add-flow s5 cookie=0x1,dl_type=0x0800,nw_proto=6,nw_dst=10.0.4.0/24,actions=output:4')

    switch6 = net.get('s6')
    switch6.cmd('sudo ovs-ofctl add-flow s6 cookie=0x1,dl_type=0x0800,nw_proto=6,nw_dst=10.0.10.10,actions=output:1')
    switch6.cmd('sudo ovs-ofctl add-flow s6 cookie=0x1,dl_type=0x0800,nw_proto=6,nw_dst=10.0.3.0/24,actions=output:2')
    switch6.cmd('sudo ovs-ofctl add-flow s6 cookie=0x1,dl_type=0x0800,nw_proto=6,nw_dst=10.0.4.0/24,actions=output:3')
    switch6.cmd('sudo ovs-ofctl add-flow s6 cookie=0x1,dl_type=0x0800,nw_proto=6,nw_dst=10.0.1.0/24,actions=output:4')
    switch6.cmd('sudo ovs-ofctl add-flow s6 cookie=0x1,dl_type=0x0800,nw_proto=6,nw_dst=10.0.2.0/24,actions=output:4')


    print "Dumping host connections"
    
    
    print "\n\n\n\n\n"
    count = 1
    for h in net.hosts:
	ip = h.cmd('ifconfig | grep "inet add" | cut -d ":" -f2 | cut -d " " -f1 | head -1')
	mac= h.cmd('ifconfig | grep "HWaddr" | cut -d "W" -f2 | cut -d " " -f2 | head -1')
	print 'sudo arp -s ' + ip.strip() + ' ' + mac.strip() + ' &'
	server.cmd('sudo arp -s ' + ip.strip() + ' ' + mac.strip() + ' &')
	h.cmd('sudo arp -s 10.0.10.10 00:00:00:00:00:01 & ')
	if not h.name in [ 'lg1', 'lg2' , 'server'] :
		print h
		print h.cmd('sudo python ~/attack.py '+ ' ~/attack/parsed/'+ str(count)  + '.csv  &') , '--'
		count = count+1
    time.sleep(1)
    print "Testing network connectivity"
    print h.cmd('sudo python ~/attack.py '+ ' ~/attack/parsed/'+ str(count)  + '.csv  &') , '--'
    lg1 = net.get('lg1')
    print lg1.cmd("~/res.sh")
    lg2 = net.get('lg2')
    print lg2.cmd("~/res.sh")
    CLI(net)

if __name__ == '__main__':
    setLogLevel( 'info' )
    perfTest()