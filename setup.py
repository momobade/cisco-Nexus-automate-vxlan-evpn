from distutils.core import setup

setup(
    # Application name:
    name="Auto-VxLan",

    # Version number (initial):
    version="0.0.1",

    # Application author details:
    author="Mohamad Mobader",
    author_email="momobade@cisco.com",

    # Packages
    packages=["app"],

    # Include additional files into the package
    include_package_data=True,

    # Details
    # url="http://pypi.python.org/pypi/MyApplication_v010/",

    #
    # license="LICENSE.txt",
    description="VxLAN parameters for underlay and overlay configuration and output the parameters into any device that supports VxLAN",

    # long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    install_requires=[ pandas, xlrd ],
)
