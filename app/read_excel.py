#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 20:57:36 2018

@author: momobade
"""

import pandas as pd
import numpy as np
import global_header as gh
import vxlan_config as vx
import underlay as un

device_list = []

def call_device_list(_device):

    for device in device_list:
        if _device == device.hostname:
            return device

    _dev = gh.device(_device)
    device_list.append(_dev)
    return _dev


#
# Function defined to read from excel sheet directly
#
def read_bgp(_srcExcel):
    bgp_info = pd.read_excel(_srcExcel, sheet_name='BGP',header=[1])

    # Fill Nan with first value in columns
    bgp_info.fillna(method='ffill', inplace=True)

    bgp_info['BGP AS Number'] = bgp_info['BGP AS Number'].astype(int)

    # Transform all values into strings
    bgp_info = bgp_info.astype(str)

    # Replace '-' with np.Nan
    bgp_info.replace(to_replace='-',value=np.NaN, inplace=True)

    bgp_info = bgp_info.where(pd.notnull(bgp_info), None)

    return bgp_info

#
# Function defined to read from excel sheet directly
#
def read_portChannel(_srcExcel):
    portChannel_info = pd.read_excel(_srcExcel, sheet_name='Fabric Port-channel', header=[1])

    # Fill Nan with first value in columns
    portChannel_info.fillna(method='ffill', inplace=True)

    portChannel_info['Port-channel'] = portChannel_info['Port-channel'].astype(int)


    # Transform all values into strings
    portChannel_info = portChannel_info.astype(str)

    # Replace '-' with np.Nan
    portChannel_info.replace(to_replace='-',value=np.NaN, inplace=True)

    portChannel_info['Native VLAN'] = (
            portChannel_info['Native VLAN'].fillna('0').astype(int).astype(str).replace(to_replace='0', value=np.NaN)
            )

    portChannel_info['vpc'] = (
            portChannel_info['vpc'].fillna('0').astype(int).astype(str).replace(to_replace='0', value=np.NaN)
            )

    portChannel_info = portChannel_info.where(pd.notnull(portChannel_info), None)

    # Identify the devices listed in the excel sheet
    output = portChannel_info['Device'].unique()

    return portChannel_info

#
# Function defined to use read from excel sheet directly
#
def read_vlan(_srcExcel):
    vlan_info = pd.read_excel(_srcExcel, sheet_name='VLAN', header=[1])

    # Fill Nan with first value in columns
    vlan_info.fillna(method='ffill', inplace=True)

    vlan_info['Vlan Number'] = vlan_info['Vlan Number'].astype(int)

    # Replace '-' with np.Nan
    vlan_info.replace(to_replace='-',value=np.NaN, inplace=True)

    vlan_info['L3VNI'] = (
            vlan_info['L3VNI'].fillna('0').astype(int).astype(str).replace(to_replace='0', value=np.NaN)
            )

    vlan_info = vlan_info.where(pd.notnull(vlan_info), None)

    # Identify the devices listed in the excel sheet
    output = vlan_info['Device'].unique()

    return vlan_info

#
# Function defined to read from excel sheet directly
#
def read_ethernet(_srcExcel):
    eth_info = pd.read_excel(_srcExcel, sheet_name='Physical interface', header=[1])

    # Fill Nan with first value in columns
    eth_info.fillna(method='ffill', inplace=True)

    # Replace '-' with np.Nan
    eth_info['Port-Channel'] = eth_info['Port-Channel'].replace(to_replace='-', value='0').astype(int).replace(to_replace='0', value=np.NaN)

    # Replace '-' with np.Nan
    eth_info.replace(to_replace='-',value=np.NaN, inplace=True)

    output = eth_info['Device'].unique()

    return eth_info

#
# Function defined to use read from excel sheet directly
#
def read_vpc(_srcExcel):
    vpc_info = pd.read_excel(_srcExcel, sheet_name='vPC', header=[1])

    vpc_info['Domain'] = vpc_info['Domain'].astype(int)
    vpc_info['Peer-Link'] = vpc_info['Peer-Link'].astype(int)
    vpc_info['Priority'] = vpc_info['Priority'].astype(int)
    vpc_info['System Priority'] = vpc_info['System Priority'].astype(int)

    output = vpc_info['Device'].unique()

    return vpc_info

def read_multicast(_srcExcel):
    multicast_info = pd.read_excel(_srcExcel, sheet_name='Multicast')

    return multicast_info

def read_ospf(_srcExcel):
    ospf_info = pd.read_excel(_srcExcel, sheet_name='OSPF')

    return ospf_info

###############################################################################
#
# Function defined to use the output of read_bgp as its input
#
def populate_bgp(df):
    #
    # Read from BGP DataFrame
    # Columns = 'Device' 'Router-ID' 'BGP AS Number' 'VRF' 'Neighbors' 'Remote AS' Route-Map OUT'
    #           'Route-map IN' 'Route-Reflector'
    #

    device_name = df['Device'].unique()

    for dev in device_name:
        _device = df[df['Device'] == dev]

        _bgp = vx.bgp(
                _device['BGP AS Number'].iloc[0],
                _device['Router-ID'].iloc[0]
                )

        # Add VRFs name to each BGP instance
        for _vrf in _device.VRF.dropna():
            _bgp.add_vrf(_vrf)

        # Add neighbors for each BGP instance
        for _itr in _device.Neighbors.dropna().index:
            _nei = vx.bgp_neighbor(
                    IP_Address = _device.Neighbors.loc[_itr],
                    remote_AS = _device['Remote AS'].loc[_itr]
                    )

            _nei.set_route_map_IN(_device['Route-Map IN'].loc[_itr])

            _nei.set_route_map_OUT(_device['Route-Map OUT'].loc[_itr])

            _nei.set_source(_device['Soure Interface'].loc[_itr])

            _nei.set_vrf(_device['VRF'].loc[_itr])

            _nei.set_RR(_device['Route-Reflector'].loc[_itr])

            _nei.set_bfd(True)

            _nei.set_password(_device['Password'].loc[_itr])

            _bgp.add_neighbor(_nei)

        # Check if the device instance is already created;
        # If yes, return the device instance
        # if not, create a new instance and append it to the list
        _node = call_device_list(dev)

        # Assign the new BGP instance to the node in the list
        _node.add_bgp(_bgp)

    return device_list

#
# Function defined to use the output of read_vlan as its input
#
def populate_vlan(df):
    vlan_ins = []

    device_name = df['Device'].unique()

    for dev in device_name:
        _device = df[df['Device'] == dev]

        for _in in _device['Vlan Number'].index:
            _vlan = vx.vlan(
                    _device['vlan name'].loc[_in],
                    _device['Vlan Number'].loc[_in]
                    )

            _vlan.setIP(
                    _device['IP address'].loc[_in],
                    _device['VRF'].loc[_in]
                    )

            if _device['L3VNI'].loc[_in] is not None:
                _vlan.to_l3vni(
                        _device['L3VNI'].loc[_in]
                        )
            else:
                _vlan.to_l2vni(
                        '1110',
                        _device['mcast_group'].loc[_in])

            # Check if the device instance is already created;
            # If yes, return the device instance
            # if not, create a new instance and append it to the list
            _node = call_device_list(dev)
            _node.add_vlan(_vlan)

    return device_list

def populate_portChannel(df):

    device_name = df['Device'].unique()

    for dev in device_name:
        _device = df[df['Device'] == dev]

        for _in in _device['Port-channel'].index:

            _po = un.port_channel(
                    _device['Port-channel'].loc[_in],
                    _device['LACP Fallback'].loc[_in],
                    _device['description'].loc[_in],
                    )

           #print(_device['vpc'].loc[_in] == '0')
            if (_device['vpc'].loc[_in] != '0'):
                _po.set_vpc(_device['vpc'].loc[_in])

            if _device['Port Type'].loc[_in] == 'Layer3':
                _po.set_layer3(
                        _device['IP Address'].loc[_in],
                        _device['VRF'].loc[_in]
                        )
            elif _device['Port Type'].loc[_in] == 'Trunk':
                _po.set_trunk(
                        _device['VLAN List'].loc[_in],
                        _device['Native VLAN'].loc[_in],
                        )
            elif _device['Port Type'].loc[_in] == 'Access':
                _po.set_access(_device['VLAN List'].loc[_in])

            elif _device['Port Type'].loc[_in] == 'dot1q':
                _po.set_dot1q(_device['VLAN List'].loc[_in])

            _node = call_device_list(dev)
            _node.add_portChannel(_po)

    return device_list

def populate_ethernet(df):

    device_name = df['Device'].unique()

    for dev in device_name:
        _device = df[df['Device'] == dev]

        for _in in _device['Interface'].index:

            _eth = un.ethernet(
                    _device['Interface'].loc[_in],

                    _device['Description'].loc[_in]
                    )
            _eth.set_lacpMode(_device['LACP'].loc[_in], _device['Port-Channel'].loc[_in])

            _node = call_device_list(dev)
            _node.add_ethernet(_eth)

    return device_list

def populate_vpc(df):

    device_name = df['Device'].unique()

    for dev in device_name:
        _device = df[df['Device'] == dev]

        for _in in _device['Domain'].index:
            _vpc = un.vpc(
                    _device['Domain'].loc[_in],
                    _device['Priority'].loc[_in],
                    _device['System Priority'].loc[_in]
                    )
            _vpc.set_peer_link(_device['Peer-Link'])

            _vpc.set_keepalive_source(
                    _device['PeerKeepalive source'].loc[_in],
                    _device['PeerKeepalive destination'].loc[_in],
                    _device['vrf'].loc[_in]
                    )

            _node = call_device_list(dev)
            _node.add_vpc(_vpc)

    return device_list

def populate_multicast(df):

    device_name = df['Device'].unique()

    for dev in device_name:
        _device = df[df['Device'] == dev]

        for _in in _device['Router-id'].index:
            _multicast = un.multicast(
                    _device['Router-id'].loc[_in],
                    _device['Anycast-RP'].loc[_in],
                    _device['Multicast Group'].loc[_in],
                    _device['isRP'].loc[_in]
                    )
            for _int in _device['Interfaces'].loc[_in].split(','):
                _multicast.add_interface(_int)

            _node = call_device_list(dev)
            _node.add_multicast(_multicast)

    return device_list

def populate_ospf(df):

    device_name = df['Device'].unique()

    for dev in device_name:
        _device = df[df['Device'] == dev]

        for _in in _device['router-id'].index:
            _ospf = un.ospf(
                    _device['process-id'].loc[_in],
                    _device['router-id'].loc[_in]
                    )
            for _int in _device['interface'].loc[_in].split(','):
                _ospf.add_interface(_int,'0.0.0.0')

            _node = call_device_list(dev)
            _node.add_ospf(_ospf)

    return device_list

###############################################################################
## MAIN Function
##

# Would probably convert this into a class with function get_configs_all
#device_list = []
#file_source = 'ip_information.xlsx'


#populate_vlan(read_vlan(file_source))
#populate_bgp(read_bgp(file_source))
#populate_portChannel(read_portChannel(file_source))
#populate_ospf(read_ospf(file_source))
#populate_multicast(read_multicast(file_source))
#populate_ethernet(read_ethernet(file_source))
#populate_vpc(read_vpc(file_source))
