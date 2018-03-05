# VxLAN Python Package

The project's purpose is to build a python package that can store VxLAN parameters for underlay and overlay configuration and output the parameters into any device that supports VxLAN. Currently the deployment is tested on Nexus 9000 switches which are widely deployed in the data center as VxLAN capable switches. The pacakge includes an input script that reads from an excel file in order to populate the VxLAN parameters.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

This software requires python 3.5 and above

Check the version of python running on the OS
```
python --version
Python 3.5.3
```
If the output is not 3.5 and above, please refer to the Installation section below

### Installing

The only requirement is to have python 3.5 running on the machine.

Please follow the below guide in order to install Python 3.5 on your machine

### Macintosh Machine

```
pip install python
```

## Running the package

The code is provided with a sample excel file which contains configuration parameters for the devices in VxLAN network. Each sheet from the excel file represent the protocol used to form the VxLAN fabric.

The program then generates text files containing the device complete configuration. The number of text files is linked to the number of devices provided in the excel file (in this example, we have four devices 'Spine1', 'Spine2', 'Leaf1, and 'Leaf2')

Run the following command in order to generate the text file samples

```
python generate_config.py -s ip_information.xlsx
```

The above command will generate four txt files which contains all the parameters of the ip_information.xlsx file.
