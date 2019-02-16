[![Coverage Status](https://coveralls.io/repos/github/quantstamp/universal-solc-compiler/badge.svg?branch=HEAD&t=ZsRMQa&service=github)](https://coveralls.io/github/quantstamp/universal-solc-compiler?branch=HEAD)
![AWS Codebuild](https://codebuild.us-east-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiRnFkajBtLzI2Y21qQ1VkZW0xdWFBMFRFcS9aVXhEZ081U0p0TStjcFRhTUtkeW44am5VT1RaU1RvTm9SZGFRWmtnUnpoblNkWDh2ME5nSFNCenZIaitnPSIsIml2UGFyYW1ldGVyU3BlYyI6Im44cmkrLzhVQWxqNzhqeEEiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=master)

# Universal Solc Compiler

Universal Solc Compiler (usolc) is a set of scripts that can be used exactly as the original solc compiler with the additional feature of reading the pragma line in the solidity file and summons the solc version that can compile the file.
The current version of usolc supports 0.4.11 ~ 0.5.3.

## Components
This tool mainly consists of 3 parts:

1. A bash script that downloads different versions of solc
2. A python program that detects the version requirement from the solidity file 
3. A Dockerfile that demonstrates how to put the tool inside of a container

## Install

### Using Docker

Prerequisite: [Docker](https://www.docker.com/)

do `make build` to build the docker image, then do `make run` to invoke the shell. The docker script will copy all the files in the same directory, therefore you could put the Solidity files you wanted to test in the same directory of the docker script.
1. Copy the files to the same directory as the Docker script.
2. do `make build`
3. do `make run` to invoke shell, see the `Usage` section on how to run usolc

### On local machine (Unix)

Prerequisite: Python3 & pip3

1. Install the requirements (`node-semver 0.6.1`)
    1. `pip3 install -U 'node-semver==0.6.1' `
2. Create solc-versions directory: `mkdir /usr/local/bin/solc-versions`
3. Download all the solc versions: `./usolc/solc_download`
4. Copying usolc scripts to proper location: 
    1. `cp ./usolc/usolc.py /usr/local/bin/solc-versions/usolc.py`
    2. `cp -r ./usolc/exceptions /usr/local/bin/solc-versions/exceptions`
    3. `cp ./usolc/solc /usr/local/bin/solc`

### On local machine (Mac)

Prerequisite: [Docker](https://www.docker.com/)

Unfortunately, usolc currently doesn't support macOS directly due to: 
1. There is [no official solidity binaries for macOS](https://github.com/ethereum/solidity/issues/3168).
According to the issue, Ethereum developers currently have no capacities to support macOS according to a discussion related to the issue. 
1. There are errors when compiling from source code [after 0.4.x](https://github.com/ethereum/solidity/issues/5414).
The issue is fixed after 0.5.0, but there are no plan from the Ethereum developers of releasing fix for 0.4.x.
1. Homebrew installation is corrupted for 0.4.25, Ethereum has [an ongoing issue](https://github.com/ethereum/solidity/issues/5452) 
that is trying to solve this problem.

For now, the workaround is using a docker image with entry point pointint to the usolc and mounts the current directory.
Therefore there are some limitations: it can only compile the files that are under the current working directory.

Installation step:
1. Remove solc in `/usr/local/bin` if it existed.
1. run shell script ./install_usolc_docker.sh

## Usage
When it is properly installed or invoked by Docker, simply call solc in the shell and it will invoke the usolc program.

> `solc ..... xxx.sol ... (-U [userRule])`

An additional parameter `-U [userRule]` is added to the usolc program. User can also enforce rules on the versions they wanted to use. The version is now chosen with the following flow:

1. usolc has a list of Available versions
2. If there is a solidity file in the argument, then the list is filtered with the pragma version statement
3. If user have specified additional rules, then the list is further filtered with the rules
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

Note that if solidity file is not provided in the argument, then it will only filter by the user's rules. 
Therefore the version selected may not be the same as the version queried by `solc --version`. 
e.g. `solc --version` will by default will select the newest version and thus may show `0.5.2`, 
but the solc version selected by the command `solc xxx.sol --version` may be `0.4.25` if the pragma line in `xxx.sol` requires `^0.4.18`

To view additional information when running `usolc`, another flag `-uinfo` is provided. 
This will show you the versions that are available and the final version that is selected. 
The difference are shown in the example below:

```
/app # solc --version
solc, the solidity compiler commandline interface
Version: 0.5.3+commit.10d17f24.Linux.g++
```

```
/app # solc -uinfo --version
#################################################
Available solc versions are: ['0.5.3', '0.5.2', '0.5.1', '0.5.0', '0.4.25', '0.4.24', '0.4.23', '0.4.22', '0.4.21', '0.4.20', '0.4.19', '0.4.18', '0.4.17']
solc version: 0.5.3
#################################################
solc, the solidity compiler commandline interface
Version: 0.5.3+commit.10d17f24.Linux.g++
```

## The source of solc binaries

* For solc versions above 0.4.10, the Ethereum Foundation has provided official linux binaries. 
* For solc versions 0.4.0 ~ 0.4.9, the binaries are compiled on the Alpine docker image and made static using [this method](https://github.com/rainbreak/solidity-static) from source and are uploaded to this repository.  

If you have doubts in the provided binaries for 0.4.0 ~ 0.4.9, we suggest that you compile the binaries directly from Ethereum's repository.

```
git clone --recursive https://github.com/ethereum/solidity.git
cd solidity
git checkout v0.x.x
git submodule update --init --recursive
./scripts/install_deps.sh
cmake .
make
```


## To install a new version of solc

To install a new version of solc on the container, one needs to modify the ardcoded list in `usolc/solc_version_list`.

Separate each version with a new line.
