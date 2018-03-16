import global_header
import read_excel as re
import sys
import getopt
import argparse

def create_parser():
    """ return  command line argument parser """
    parser = argparse.ArgumentParser(description='VxLan Tool')
    parser.add_argument('file', help="source file")
    return parser

def main(argv):
    parser = create_parser()
    args = parser.parse_args()
    sourcefile = args.file

    device_list = []
    device_list = re.populate_vlan(re.read_vlan(sourcefile))
    device_list = re.populate_bgp(re.read_bgp(sourcefile))
    device_list = re.populate_portChannel(re.read_portChannel(sourcefile))
    device_list = re.populate_ospf(re.read_ospf(sourcefile))
    device_list = re.populate_multicast(re.read_multicast(sourcefile))
    device_list = re.populate_ethernet(re.read_ethernet(sourcefile))
    device_list = re.populate_vpc(re.read_vpc(sourcefile))

    for dev in device_list:
        ## save original stdout
        orig_stdout = sys.stdout

        f = open(dev.hostname+'.txt', 'w')
        sys.stdout = f
        print(dev)
        print(dev.show_config_all())

        sys.stdout = orig_stdout
        f.close()

if __name__ == "__main__":
    main(sys.argv[1:])
