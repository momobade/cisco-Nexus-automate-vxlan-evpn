import global_header
import read_excel as re
import sys


def main():
    device_list = []
    file_source = 'ip_information.xlsx'

    device_list = re.populate_vlan(re.read_vlan(file_source))
    device_list = re.populate_bgp(re.read_bgp(file_source))
    device_list = re.populate_portChannel(re.read_portChannel(file_source))
    device_list = re.populate_ospf(re.read_ospf(file_source))
    device_list = re.populate_multicast(re.read_multicast(file_source))
    device_list = re.populate_ethernet(re.read_ethernet(file_source))
    device_list = re.populate_vpc(re.read_vpc(file_source))

    for _device in device_list:
        ## save original stdout
        orig_stdout = sys.stdout

        f = open(_device.hostname+'.txt', 'w')
        sys.stdout = f
        print(_device.show_config_all())

        sys.stdout = orig_stdout
        f.close()

if __name__ == '__main__':
    main()
