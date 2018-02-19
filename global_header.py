#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 16 18:54:44 2018

@author: momobade
"""

class device:
    def __init__(self, hostname):
        self.hostname = hostname
        self.vlan_list = []
        self.VRF = []
        self.PO = []
        self.intf = []
        
        self.ospf = None
        self.multicast = None
        self.bgp = None
        self.vpc = None
    
    def add_vlan(self, vlan):
        self.vlan_list.append(vlan)
    
    def conf_bgp(self, BGP):
        self.BGP = BGP
    
    def add_vrf(self, VRF):
        self.VRF.append(VRF)
        
    def add_ospf(self, OSPF):
        self.OSPF = OSPF

    def add_multicast(self, Multicast):
        self.multicast = Multicast
    
    def add_portChannel(self, PortChannel):
        self.PO.append(PortChannel)
    
    def add_ethernet(self, ethernet):
        self.intf.append(ethernet)
        
    def add_vpc(self, vpc):
        self.vpc = vpc
    
    def show_config_all(self):
        config = (
                "## Device Configuration : %s##\n"
                "hostname %s\n!\n"%(self.hostname, self.hostname))
        if self.vlan_list:
            for _vlan in self.vlan_list:
                config = config + _vlan.config
        if self.VRF:
            for _vrf in self.VRF:
                config = config + _vrf.config
        if self.PO:
            for _po in self.PO:
                config = config + _po.show_config()
        if self.intf:
            for _intf in self.intf:
                config = config + _intf.show_config()
        if self.BGP is not None:
            config = config + self.BGP.config
        if self.OSPF is not None:
            config = config + self.OSPF.config
        if self.multicast is not None:
            config = config + self.multicast.show_config()
        if self.vpc is not None:
            config = config + self.vpc.show_config()
        
        return config