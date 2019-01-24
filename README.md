# Universal Solc Compiler


## Components
This tool mainly consists of 3 parts:

1. A bash script that downloads different versions of solc
2. A python program that detects the version requirement from the solidity file 
3. A Dockerfile that demonstrates how to put the tool inside of a container


## Usage
When it is properly installed, simply call solc in the shell and it will invoke the usolc program.

> `solc ..... xxx.sol ... (-U [userRule])`

An additional parameter `-U [userRule]` is added to the usolc program. User can also enforce rules on the versions they wanted to use. The version is now chosen with the following flow:

1. usolc has a list of Available versions
2. The list is filtered with the solidity pragma version statement
3. If specified, then the list is further filtered with the user specified rules
4. Choose the newest version available in the resulting list

`userRule` is in the format of `[version filter](+-)`

Semantic versioning can be used in the `[version filter]`, 
where `+` indicates "prefer newest compiler", `-` indicates "prefer oldest compiler".
if + or - is not indicated, then the default would be "prefer newest compiler"

Here are some examples:

| Commands | Meaning |
| -------- | ------- |
| `solc ....... -U 0.4.2`    |      use compiler 0.4.2              |
| `solc ....... -U 0.4.*`    |      use newest compiler in 0.4.*    |
| `solc ....... -U 0.4.*+`   |      use newest compiler in 0.4.*   |
| `solc ....... -U 0.4.*-`   |      use oldest compiler in 0.4.*   |
| `solc ....... -U +`        |      use newest compiler available  |
| `solc ....... -U -`        |      use oldest compiler available  | 
| `solc ....... -U ">0.4.2 <0.6.0+"`|use newest compiler available that satisfies `>0.4.2 <0.6.0` | 

## To install a new version of solc

To install a new version of solc on the container, one needs to modify the following two hardcoded lists:

1. SOLCVERSION in solc_download
2. valid_versions in usolc.py

