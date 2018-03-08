#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 16 18:53:31 2018

@author: momobade
"""

import vxlan_config as vx
import global_header as gh

class ospf:
    def __init__(self, processID, routerID):
        self.RID = routerID
        self.PID = processID
        self.interfaces = []
        # initiate variable config
        self.config = ("router ospf %s"
                     "\n router-id %s"
                     "\n log-adjacency-changes detail"
                     "\n timers throttle spf 100 100 5000"
                     "\n timers lsa-arrival 15"
                     "\n timers throttle lsa 0 50 5000"
                     "\n auto-cost reference-bandwidth 400 Gbps\n !\n"
                     %(self.PID, self.RID))
    
    def add_interface(self, intf, area):
        self.config = (
                self.config +
                "interface %s"
                "\n ip router ospf %s area %s\n!\n"
                %(intf, self.PID, area)
                )

    def show_config(self):
        print(self.config)
    

class multicast:
    def __init__(self, routerID, AnycastRP, Multicast_Group, isRP):
        self.RID = routerID
        self.AnycastRP = AnycastRP
        self.MG = Multicast_Group
        self.RP = isRP
        self.intf = []
    
    def add_interface(self, intf):
        self.intf.append(intf)
    
    def set_RP(self):
        self.RP = True
    
    def show_config(self):
        config = (
                "ip pim rp-address %s group-list %s\n!\n"
                %(self.AnycastRP, self.MG)
                )
        if self.RP:
            config = (config + "ip pim anycast-rp %s %s\n!\n"
                      %(self.AnycastRP,self.RID)
                      )
        
        for _int in self.intf:
            config = ( config +
                      "interface %s\n"
                      " ip pim sparse-mode\n!\n"
                      %(_int)
                      )
        return config

class port_channel:
    def __init__(self, number, lacpFallback, description):
        self.number = number
        self.desc = description
        self.lacpFallback = True if lacpFallback == 'Yes' else False
        
        # default values
        self.portType = 0
        self.vpc = None

        ##  portType values:
        ##      0   : Not Defined --> default value
        ##      1   : Layer 3
        ##      2   : Trunk
        ##      3   : Access
        ##      4   : Dot1q
    
    def set_layer3(self, IP_Address, VRF):
        self.portType = 1
        self.IP = IP_Address
        self.VRF = VRF
    
    def set_trunk(self, vlanList, nativeVLAN = None):
        self.portType = 2
        self.vlanList = vlanList
        self.nativeVLAN = nativeVLAN
    
    def set_access(self, vlanList):
        self.portType = 3
        self.accessVLAN = vlanList
    
    def set_dot1q(self, vlanList):
        self.portType = 4
        self.vlanList = vlanList
    
    def set_vpc(self, vpc_number):
        self.vpc = vpc_number
    
    def show_config(self):
        config = (
                "interface Port-channel %s\n"
                " description %s\n"
                " no shutdown\n"
                " mtu 9178\n"
                %(self.number,self.desc)
                )
        
        if self.vpc is not None:
            config = config + " vpc "+ self.vpc+"\n"
        
        if self.lacpFallback:
            config = ( config +
                    " no lacp suspend-individual\n"
                    " no lacp graceful-convergence\n"
                    )
        if self.portType is 0:  # Not Defined
            print(config)
        
        if self.portType is 2:
            config = ( config +
                    " switchport\n"
                    " switchport mode trunk\n"
                    " switchport trunk allowed vlan %s"
                    %(self.vlanList))
            config = config +" switchport trunk native vlan %s"%(self.nativeVLAN) if self.nativeVLAN is not None else config
            
            config = config + "\n!\n"
        
        if self.portType is 3:
            config = ( config +
                    " switchport\n"
                    " switchport mode access\n"
                    " switchport access vlan %s\n!\n"
                    %(self.accessVLAN))
        
        if self.portType is 4:  # dot1q encapsulation
            config = (
                    " interface port-channel %s.%s\n"
                    " description %s\n"
                    " encapsulation dot1q %s\n!\n"
                    %(self.number, self.vlanList, self.desc, self.vlanList))
        
        if self.portType is 1:  # Layer3
            config = ( config +
                    " no switchport\n"
                    " vrf member %s\n"
                    " ip address %s\n!\n"
                    %(self.VRF, self.IP))
        
        return config
        
class ethernet:
    def __init__(self, intf_name, description):
        self.name = intf_name
        self.desc = description
        self.trunk = False
        self.access = False
        self.vlanList = None
        self.nativeVlan = None
    
    def set_lacpMode(self, lacpMode, port_channel):
        self.lacpMode = lacpMode
        self.po = port_channel
    
    def set_trunk(self, vlan_list, nativeVlan = None):
        self.vlanList = vlanList
        self.nativeVlan = nativeVlan
        self.trunk = True
    
    def set_access(self, vlan):
        self.vlanList = vlan
        self.access = True
    
    def show_config(self):
        config = (
                "interface %s\n"
                " description %s\n"
                " no shutdown\n"
                %(self.name, self.desc))
        
        if self.lacpMode == 'Active':
            config = ( config + 
                    " channel-group %s mode active\n!\n"
                    %(self.po))
            return config

        if self.lacpMode == 'On':
            config = ( config +
                    " channel-group %s mode on\n!\n" 
                    %(self.po))
            return config
        
        if self.trunk:
            config = ( config +
                    " switchport\n"
                    " switchport mode trunk\n"
                    " switchport trunk allowed vlan %s\n"
                    " switchrpot trunk native vlan %s\n!\n"
                    %(self.vlanList, self.nativeVlan))
        
        if self.access:
            config = ( config +
                    " switchport\n"
                    " switchport mode access\n"
                    " switchport access vlan %s\n!\n"
                    %(self.vlanList))
        
        return config

class vpc:
    def __init__(self, domain, priority, system_priority):
        self.domain = domain
        self.priority = priority
        self.system_priority = system_priority
    
    def set_peer_link(self, peer_link):
        self.peer_link = peer_link
    
    def set_keepalive_source(self, keepalive_source, keepalive_destination, keepalive_vrf):
        self.keepalive_source = keepalive_source
        self.keepalive_destination = keepalive_destination
        self.keepalive_vrf = keepalive_vrf
    
    def show_config(self):
        config = (
                "vpc domain %s\n"
                " peer-switch\n"
                " role priority %s\n"
                " system-priority %s\n"
                " peer-keepalive destination %s source %s vrf %s\n"
                " peer-gateway\n"
                " ipv6 nd synchronize\n"
                " ip arp synchronize\n!\n"
                "interface port-channel %i\n"
                " vpc peer-link\n!"
                %(self.domain, self.priority , self.system_priority, self.keepalive_destination,
                  self.keepalive_source, self.keepalive_vrf, self.peer_link))
        
        return config
