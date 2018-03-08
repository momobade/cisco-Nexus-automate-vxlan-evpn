#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 20:57:36 2018

@author: momobade
"""

## Specify if neigbour under bgp has l2vpn evpn address-family
##

class vlan:
    def __init__(self, _name, _number, _vrf=None):
        self.number = _number if type(_number) is str else str(_number)
        self.name = _name
        self.vrf = 'default'
        self.IP = None
        self.vn_segment = None
        self.mcast_group = None
        self.rd = None
        self.rt = None
        self.isl2vni = False
        self.isl3vni = False

    def __str__(self):
        return self.name
    
    def setIP(self, IP_Address, vrf = 'default'):
        self.IP = IP_Address
        self.vrf = vrf
        
    def to_l2vni(self, tag, mcast_group, rd = 'auto', rt = 'auto'):
        self.tag = str(tag) if type(tag) is str else tag
        self.vn_segment = self.tag + self.number
        self.mcast_group = mcast_group
        self.rd = rd
        self.rt = rt 
        self.isl2vni = True
        self.isl3vni = False
        
    def to_l3vni(self, vn_segment):
        #
        # vn_segment should be the vni tag associated with the VRF
        #
        self.vn_segment = vn_segment
        
        # L3VNI has no IP address, setting IP to None
        self.IP = None
        
        self.isl3vni = True
        self.isl2vni = False
        
    def is_l2vni(self):
        return self.isl2vni
    
    def is_l3vni(self):
        return self.isl3vni

    def show_config(self):
        config = ( "vlan %s\n"
                %(self.number))
        
        if self.name is not None:
            config = (config +
                    " name %s\n" 
                    %(self.name))
        
        if self.vn_segment is not None:
            config = ( config +
                    " vn-segment %s\n!\n"
                    %(self.vn_segment))
        
        if self.IP is not None:
            config = ( config +
                    "interface vlan %s\n"
                    " description interface_%s\n"
                    " vrf member %s\n"
                    " ip address %s\n"
                    " no shutdown\n"
                    " fabric forwarding mode anycast-gateway\n!\n"
                    %(self.number, self.name, self.vrf, self.IP))
            
        if self.isl2vni:
#            config = ( config +
#                    "vlan %s\n"
#                    " name %s\n"
#                    " vn-segment %s\n!\n"
#                    %(self.number, self.name, self.vn_segment))
            
            config = ( config +
                    "evpn\n"
                    " vni %s l2\n"
                    "  rd %s\n"
                    "  route-target both %s\n !\n!\n"
                    %(self.vn_segment, self.rd, self.rt))
        
            config = (config +
                     "interface nve1\n"
                     " member vni %s\n"
                     "  suppress-arp\n"
                     "  mcast-group %s\n !\n!\n"
                    %(self.vn_segment, self.mcast_group))
        
        if self.isl3vni:
#            config = ( config +
#                    "vlan %s\n"
#                    " name %s\n"
#                    " vn-segment %s\n!\n"
#                    %(self.number, self.name, self.vn_segment))
            
            config = ( config +
                    "interface vlan %s\n"
                    " description l3vni_interface_%s\n"
                    " vrf member %s\n"
                    " ip forward\n"
                    " no shutdown\n!\n"
                    %(self.number, self.name, self.vrf))
        
            config = (config +
                     "interface nve1\n"
                     " member vni %s associate-vrf\n !\n!\n"
                    %(self.vn_segment))
        
        return config

class bgp_neighbor:
    def __init__(self, IP_Address, remote_AS):
        self.IP = IP_Address
        self.AS = remote_AS
        self.source = None
        self.vrf = None
        self.isRR = False
        self.rmIN = None
        self.rmOUT = None
        self.loopback = None
        self.password = None
        self.bfd = False
    
    def set_route_map_IN(self, route_map_IN):
        self.rmIN = route_map_IN
    
    def set_route_map_OUT(self, route_map_OUT):
        self.rmOUT = route_map_OUT

    def set_source(self, source):
        self.source = source
    
    def set_vrf(self, vrf):
        self.vrf = vrf
    
    def set_RR(self, _bool):
        self.isRR = _bool
    
    def set_password(self, password):
        self.password = password
    
    def set_bfd(self, bfd_bool):
        self.bfd = True
    
class bgp:
    def __init__(self, _asn, _routerID):
        self.ASN = _asn
        self.RID = _routerID
        self.vrf = []
        self.neighbors = []
        
    def add_vrf(self, vrf_name):
        self.vrf.append(vrf_name)
    
    def add_neighbor(self, neighbor):
        if neighbor.source is None:
            neighbor.source = self.RID
        
        self.neighbors.append(neighbor)
        
    def show_config(self):
        config = ("router bgp %s\n"
                  " router-id %s\n"
                  " address-family ipv4 unicast\n"
                  " address-family l2vpn evpn\n"
                  "  retain route-target all\n !\n"
                  %(self.ASN, self.RID))
        
        if self.vrf:
            for _vrf in self.vrf:
                config = ( config +
                          " vrf %s\n"
                          "  address-family ipv4 unicast\n"
                          "   advertise l2vpn evpn\n !\n"
                          %(_vrf))
        if self.neighbors:
            for _neighbor in self.neighbors:
                config = config + "vrf "+_neighbor.vrf+"\n " if type(_neighbor.vrf) is str else config
                config = (config + 
                          "neighbor %s remote-as %s\n"
                          "  update-source %s\n"
                          %(_neighbor.IP, _neighbor.AS, _neighbor.source))
                
                if _neighbor.bfd:
                    config = ( config + 
                              "  bfd\n"
                              )
                if _neighbor.password is not None:
                    config = ( config +
                            "  password %s\n"
                            %(_neighbor.password))
                config = (config +
                          "  address-family ipv4 unicast\n"
                          "   send-community both\n")
                
                config = config + "   route-reflector-client\n" if _neighbor.isRR else config
                
                if _neighbor.rmIN is not None:
                    config = ( config +
                            "   route-map %s in\n"
                              %(_neighbor.rmIN)
                            )
                
                if _neighbor.rmOUT is not None:
                    config = ( config +
                              "   route-map %s out\n"
                              %(_neighbor.rmOUT))
                
                config = config + "  !\n !\n"
        
        return config

class vrf:
    def __init__(self, _name, _vni, _rd='auto', _rt='auto'):
        self.name = _name
        self.VNI = _vni
        self.RD = _rd
        self.RT = _rt
        self.static_routes = []
    
    def add_static_route(self, _static_route):
        self.static_routes.append(_static_route)
    
    def show_config(self):

        config = (
                "vrf context %s\n"
                " rd %s\n"
                " vni %s\n"
                " address-family ipv4 unicast\n"
                "  route-target both %s\n"
                "  route-target both %s evpn\n"
                " !\n"
                "!\n"
                %(self.name, self.RD, self.VNI, self.RT, self.RT))
        
        return config

class static_route:
    def __init__(self):
        self.subnet = None
        self.next_hope = None
        self.description = None
        self.tag = None
        self.vrf = None
        self.route_preference = None
    
    def set_subnet(self, subnet):
        self.subnet = subnet
    
    def set_next_hop(self, next_hop):
        self.next_hope = next_hope
    
    def set_description(self, description):
        self.description = description
    
    def set_tag(self, tag):
        self.tag = tag
    
    def set_vrf(self, vrf_name):
        self.vrf = vrf
    
    def set_route_preference(self, route_preference):
        self.route_preference = route_preference
    
    def show_config(self):
        config = "vrf context %s\n " if self.vrf is not None else ""
        config = ( config +
                "ip route %s %s"
                %(self.subnet, self.next_hope))
        config = config + " name "+self.name if self.name is not None else config
        config = config + " tag "+self.tag if self.tag is not None else config
        config = config + " "+self.route_preference if self.route_preference is not None else config
        config = config + "\n!\n"
        
        return config
