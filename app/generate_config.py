import global_header
import read_excel as re
import sys


def main(argv):
    sourcefile = ''
    
    try:
        opts, args = getopt.getopt(argv, "hi:s:",["sourcefile="])
    except getopt.GetoptError:
        print('generate_config.py -s <sourcefile>')
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            print('generate_config.py -s <sourcefile>\n')
            print('<sourcefile> expects excel sheet')
            sys.exit()
        elif opt in ('-s', '--sourcefile'):
            sourcefile = arg
        
        print('sourcefile='+sourcefile)


    device_list = []
    #file_source = 'ip_information_LAB_VNF.xlsx'

    device_list = re.populate_vlan(re.read_vlan(sourcefile))
    device_list = re.populate_bgp(re.read_bgp(sourcefile))
    device_list = re.populate_portChannel(re.read_portChannel(sourcefile))
    device_list = re.populate_ospf(re.read_ospf(sourcefile))
    device_list = re.populate_multicast(re.read_multicast(sourcefile))
    device_list = re.populate_ethernet(re.read_ethernet(sourcefile))
    device_list = re.populate_vpc(re.read_vpc(sourcefile))

    for _device in device_list:
        ## save original stdout
        orig_stdout = sys.stdout

        f = open(_device.hostname+'.txt', 'w')
        sys.stdout = f
        print(_device.show_config_all())

        sys.stdout = orig_stdout
        f.close()

if __name__ == "__main__":
    main(sys.argv[1:])
