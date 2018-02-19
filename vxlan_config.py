#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 20:57:36 2018

@author: momobade
"""

class vlan:
    def __init__(self, _name, _number, _vrf=None, _ipAddress=None):
        self.number = _number if type(_number) is str else str(_number)
        self.name = _name
        self.vrf = _vrf if type(_vrf) is str else 'default'
        self.IP = _ipAddress if type(_ipAddress) is str else None
        # initiate variable config
        self.config = (
                "vlan "+self.number+"\n"
                " name "+self.name+"\n!\n"
                )
        if str(self.IP) is str:
            self.config = (
                    self.config + "interface vlan "+self.number+"\n"
                    " description interface_"+self.name+"\n")
            self.config = self.config + " vrf "+self.vrf.name+"\n" if type(self.vrf) is str else self.config
            self.config = self.config + " ip address "+self.IP+"\n no shutdown\n!\n"

    def __str__(self):
        return repr(self.name)
        
    def to_l2vni(self, tag, mcast_group, rd = 'auto', rt = 'auto'):
        self.tag = str(tag) if type(tag) is str else tag
        self.vn_segment = self.tag + self.number
        self.mcast_group = mcast_group
        self.rd = rd
        self.rt = rt
        
        # Adding vn-segment to VLAN
        self.config = self.config + "vlan "+self.number+"\n vn-segment "+self.vn_segment+"\n!\n"
        
        # Adding l2vni in evpn control-plane
        self.config = (self.config + "evpn\n vni "+self.vn_segment+" l2\n rd "+self.rd+
                       "\n  route-target both "+self.rt+
                       "\n  route-target both "+self.rt+" evpn\n !\n!\n")
        
        #Adding vni under interface nve
        self.config = (self.config + "interface nve1"+
                       "\n member vni "+self.vn_segment+
                       "\n  suppress-arp\n  mcast-group "+self.mcast_group+"\n !\n!\n")
    def to_l3vni(self, vn_segment):
        #
        # vn_segment should be the vni tag associated with the VRF
        #
        self.vn_segment = vn_segment
        try:
            self.config = self.config + "vlan "+self.number+"\n vn-segment "+self.vn_segment+"\n!\n"
            self.config = (self.config +
                           "interface vlan "+self.number+"\n"
                           " description interface_"+self.name+"\n"
                           " vrf "+self.vrf+"\n"
                           " no shutdown\n!\n"
                           )
        
        except AttributeError as _err:
            print("VLAN has no VRF/IP defined. Please define VRF/IP before converting into a L3VNI")
            print(_err)
        
    def is_l2vin(self):
        try:
            return True if self.tag is not None else False
        except:
            return False

    def show_config(self):
        return print(self.config +'!')

class bgp:
    def __init__(self, _asn, _routerID):
        self.ASN = _asn
        self.RID = _routerID
        self.vrf = []
        self.neighbors = []
        # initiate variable config
        self.config = ("router bgp %s\n"
                     " router-id %s\n"
                     " address-family ipv4 unicast\n"
                     " address-family l2vpn evpn\n"
                     "  retain route-target all\n !\n"
                     %(_asn, _routerID))
        for vrf in self.vrf:
            self.config = self.config + "vrf "+vrf.name+"\n address-family ipv4 unicast\n  advertise l2vpn evpn\n exit\nexit"
    
    def show_config(self):
        return print(self.config +'!')
    
    __show_config = show_config
    
    def add_vrf(self, _vrf):
        self.vrf.append(_vrf)
        
        self.config = (
                self.config + " vrf "+_vrf+"\n"
                " address-family ipv4 unicast\n"
                "  advertise l2vpn evpn\n !\n"
                )
    
    def add_neighbor(self, IP_Address, remote_AS, route_map_IN = None, route_map_OUT = None, vrfName=None, isRR = False):
        
        self.config = self.config + "vrf "+vrfName+"\n" if type(vrfName) is str else self.config
        self.config = (
                self.config + " neighbor " +IP_Address+" remote-as "+remote_AS+
                "\n  update-source "+self.RID
                )
        # Check Route-Reflector flag is true
        if isRR is 'True':
            self.config = (
                    self.config +
                    "\n  address-family ipv4 unicast"
                    "\n   send-community both"
                    "\n   route-reflector-client"
                    "\n  address-famili l2vpn evpn"
                    "\n   send-community both"
                    "\n   route-reflector-client\n"
                    )
        else:
            self.config = (
                    self.config +
                    "\n  address-family ipv4 unicast"
                    "\n   send-community both"
                    "\n  address-famili l2vpn evpn"
                    "\n   send-community both\n"
                    )        
        
        # If neighbor has route-maps, we add them
        self.config = self.config + "   route-map "+route_map_IN+" in\n" if type(route_map_IN) is str else self.config
        self.config = self.config + "   route-map "+route_map_OUT+" out\n" if type(route_map_OUT) is str else self.config        

        self.config = self.config + "  !\n !\n"

class vrf:
    def __init__(self, _name, _vni, _rd='auto', _rt='auto'):
        self.name = _name
        self.VNI = _vni
        self.RD = _rd
        self.RT = _rt
        # Initiating variable config
        self.config = (
                "vrf context "+self.name+"\n rd "+self.RD+
                "\n vni "+self.VNI+"\n address-family ipv4 unicast\n   "
                "route-target both "+self.RT+"\n    route-target both"+self.RT+"evpn\n   !\n  !\n !\n!\n"
                )
    
    def add_static_route(self, subnet, next_hop, name = 'None', tag='None'):
        self.config = self.config + "vrf context "+self.name+"\n ip route "+subnet+" "+next_hop
        self.config = self.config + " name "+name if type(name) is str else self.config
        self.config = self.config + " tag "+tag if type(tag) is str else self.config
    
    def show_config(self):
        return print(self.config)
    