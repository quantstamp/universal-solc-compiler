[![Coverage Status](https://coveralls.io/repos/github/quantstamp/universal-solc-compiler/badge.svg?branch=HEAD&t=ZsRMQa)](https://coveralls.io/github/quantstamp/universal-solc-compiler?branch=HEAD)
![AWS Codebuild](https://codebuild.us-east-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiRnFkajBtLzI2Y21qQ1VkZW0xdWFBMFRFcS9aVXhEZ081U0p0TStjcFRhTUtkeW44am5VT1RaU1RvTm9SZGFRWmtnUnpoblNkWDh2ME5nSFNCenZIaitnPSIsIml2UGFyYW1ldGVyU3BlYyI6Im44cmkrLzhVQWxqNzhqeEEiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=master)

# Universal Solc Compiler

## Components
This tool mainly consists of 3 parts:

1. A bash script that downloads different versions of solc
2. A python program that detects the version requirement from the solidity file 
3. A Dockerfile that demonstrates how to put the tool inside of a container

## Install

### Using Docker
do `make build` to build the docker image, then do `make run` to invoke the shell. The docker script will copy all the files in the same directory, therefore you could put the Solidity files you wanted to test in the same directory of the docker script.
1. Copy the files to the same directory as the Docker script.
2. do `make build`
3. do `make run` to invoke shell, see the `Usage` section on how to run usolc

### On local machine (Unix)
1. Install the requirements (`node-semver 0.6.1`)
    1. `pip3 install -U 'node-semver==0.6.1' `
2. Create solc-versions directory: `mkdir /usr/local/bin/solc-versions`
3. Download all the solc versions: `./usolc/solc_download`
4. Copying usolc scripts to proper location: 
    1. `cp ./usolc/usolc.py /usr/local/bin/solc-versions/usolc.py`
    2. `cp -r ./usolc/exceptions /usr/local/bin/solc-versions/exceptions`
    3. `cp ./usolc/solc /usr/local/bin/solc`

    
## Usage
When it is properly installed or invoked by Docker, simply call solc in the shell and it will invoke the usolc program.

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

To install a new version of solc on the container, one needs to modify the ardcoded list in `usolc/solc_version_list`.

Separate each version with a new line.
