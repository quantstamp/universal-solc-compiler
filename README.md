#Universal Solc Compiler


## Components
This tool mainly consists of 3 parts:

1. A bash script that downloads different versions of solc
2. A python program that detects the version requirement from the solidity file 
3. A Dockerfile that demonstrates how to put the tool inside of a container


## Usage
When it is properly installed, simply call solc in the shell and it will invoke the usolc program.

> solc ..... xxx.sol ... (-U [userRule])

An additional parameter (-U [userRule]) is added to the usolc program. User can also enforce rules on the versions they wanted to use. The version is now chosen with the following flow:

1. usolc has a list of Available versions
2. The list is filtered with the solidity pragma version statement
3. If specified, then the list is further filtered with the user specified rules
4. Choose the newest version available in the resulting list

Currently, userRule can only specify a single version, e.g. 0.4.22

> solc ..... xxx.sol ... -U 0.4.22


## To install a new version of solc

To install a new version of solc on the container, one needs to modify the following two hardcoded lists:

1. SOLCVERSION in solc_download
2. valid_versions in usolc.py

