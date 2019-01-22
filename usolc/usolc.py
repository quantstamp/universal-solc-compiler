####################################################################################################
#                                                                                                  #
# (c) 2019 Quantstamp, Inc. All rights reserved.  This content shall not be used, copied,          #
# modified, redistributed, or otherwise disseminated except to the extent expressly authorized by  #
# Quantstamp for credentialed users. This content and its use are governed by the Quantstamp       #
# Demonstration License Terms at <https://s3.amazonaws.com/qsp-protocol-license/LICENSE.txt>.      #
#                                                                                                  #
####################################################################################################

"""
 Find *.sol in the arguments, then parse the file to determine the version from first pragma
 finally, we will send all the parameters to the specific version of solc

 solc ....... -U 0.4.2           use compiler 0.4.2
 solc ....... -U 0.4.*           use newest compiler in 0.4.*
 solc ....... -U 0.4.*+          use newest compiler in 0.4.*
 solc ....... -U 0.4.*-          use oldest compiler in 0.4.* (- not supported by library)
 solc ....... -U +               use newest compiler available
 solc ....... -U -               use oldest compiler available (- not supported by library)

"""

import sys
import re
import subprocess
import semver
from enum import Enum
from exceptions.filename_not_found_in_argument import FilenameNotFoundInArgument
from exceptions.pragmaline_notfound_error import PragmaLineNotFoundError
from exceptions.noversion_available_by_sol import NoVersionAvailableBySol
from exceptions.noversion_available_by_user import NoVersionAvailableByUser


def make_semver_filter(rule_text):
    """
    Construct a filter based on the rule provided
    """
    def semver_check(x):
        return semver.satisfies(x, rule_text)

    return semver_check


def semver_filter(version_list, rule_text):
    """
    Filter the list using the rule provided
    """
    full_rule_filter = make_semver_filter(rule_text)
    filter_result = filter(full_rule_filter, version_list)
    return filter_result


pragma_solidity = re.compile(r'pragma\ssolidity\s(.*);', re.IGNORECASE)


def extract_pragma_line(filename):
    """
    Opens the file, then find the line that indicates the solidity version
    Returns that line
    """
    pragma_line = None

    with open(filename, 'r') as file:
        for line in file:
            if pragma_solidity.match(line) is not None:
                pragma_line = line
                break    
    file.close()

    if pragma_line is None:
        raise PragmaLineNotFoundError("Cannot find pragma line that specifies version")

    return pragma_line


def getrule_from_pragma(line):
    """
    Extract the rule from the version line in solidity file.
    """
    version_match = pragma_solidity.search(line)
    version_rule = version_match.group(1)

    return version_rule


def getrule_from_file(filename):
    """
    Extract the versioning rule from the solidity file
    """
    pragma_line = extract_pragma_line(filename)
    semver_rule = getrule_from_pragma(pragma_line)
    return semver_rule


def extract_arguments(sargv):
    """
    Iterate through the arguments for the universal compiler, 
    then remove them if they're not needed in the usual solc compiler
    """
    argv = sargv[1:]

    filename = None
    version_selection_strategy_str = None
    native_argv = []

    non_native = False

    for arg in argv:
        if arg == "-U":
            non_native = True
        elif non_native is True:
            version_selection_strategy_str = arg
            non_native = False
        else:
            if arg[-4:] == ".sol":
                filename = arg
            native_argv.append(arg)

    if filename is None:
        raise FilenameNotFoundInArgument("Didn't find any argument that " 
                                         "represents a solidity file.")

    version_selection_strategy = interpret_strategy_string(version_selection_strategy_str)

    return [filename, version_selection_strategy, native_argv]


class VersionChoosing(Enum):
    NEWEST = 1
    OLDEST = 2


def interpret_strategy_string(strategy_string):
    """
    Choosing strategy includes a user defined filter 
    and a preference to select the newest or oldest version possible

    This function reads the parameter string and interprets it with the following rule:

    [version filter](+-)

    semantic versioning can be used in the [version filter], 
    + indicates "prefer newest compiler", - indicates "prefer oldest compiler".

    if + or - is not indicated, then the default would be "prefer newest compiler"

    Currently, since min_satisfying is not implemented by node-semver, 
    therefore - is not functioning, it will be treated as + as well.

    """
    choosing = None
    version_filter = []

    if strategy_string is None:
        choosing = VersionChoosing.NEWEST
        version_filter = "*"
    elif strategy_string[-1] == "+":
        choosing = VersionChoosing.NEWEST
        version_filter = strategy_string[:-1]
    elif strategy_string[-1] == "-":
        # min_satisfying is not implemented by the library yet
        print("WARNING: the codebase currently doesn't support getting the oldest" 
              "version of the compilers")
        choosing = VersionChoosing.OLDEST
        version_filter = strategy_string[:-1]
    else:
        choosing = VersionChoosing.NEWEST
        version_filter = strategy_string

    return [version_filter, choosing]


def choose_version_by_strategy(target_list, version_selection_strategy):
    """
    Choose a specific version in the list, 
    according to version selection strategy specified by the user
    """
    
    [target_range, choosing] = version_selection_strategy

    if choosing == VersionChoosing.NEWEST:
        result = semver.max_satisfying(target_list, target_range, loose=True)
    else:
        # min_satisfying is not implemented by the library yet
        result = semver.min_satisfying(target_list, target_range, loose=True)

    return result


def choose_version_by_argument(available_versions, filename, version_selection_strategy):
    sol_rule = getrule_from_file(filename)
    filtered_by_sol_compiler_list = list(semver_filter(available_versions, sol_rule))
    if not filtered_by_sol_compiler_list:
        raise NoVersionAvailableBySol(
                available_versions, sol_rule,
                "No solc version that satisfies the requirement of the solidity file")

    user_rule = version_selection_strategy
    version_chosen = choose_version_by_strategy(filtered_by_sol_compiler_list,
                                                version_selection_strategy)
    if version_chosen is None:
        raise NoVersionAvailableByUser(
                available_versions, sol_rule, user_rule,
                "No solc version that satisfies both the requirement of"+
                " the solidity file and the user's rule")

    return version_chosen


def run_solc(version_chosen, native_argv):
    print("solc version: " + version_chosen)
    print("#################################################")

    subprocess.run(["/usr/local/bin/solc-versions/solc-"+version_chosen] + native_argv)


def main():
    valid_versions = ["0.5.0", "0.4.25", "0.4.24", "0.4.23", "0.4.22", "0.4.21", "0.4.20"]
    print("#################################################")
    print("Available solc versions are: " + str(valid_versions))

    try:
        [filename, version_selection_strategy, native_argv] = extract_arguments(sys.argv)
        version_chosen = choose_version_by_argument(valid_versions, filename,
                                                    version_selection_strategy)
        run_solc(version_chosen, native_argv)
        return 0
    except PragmaLineNotFoundError:
        print("Cannot find pragma line that specifies version")
    except FilenameNotFoundInArgument:
        print("Failed to detect solidity file in the arguments")
    except FileNotFoundError:
        print("Solidity file not found")
    except NoVersionAvailableBySol as e:
        print("Cannot find solc version that meets the requirement of the solidity file")
        print("Solidity file's requirement: ")
        print(e.sol_rule)
    except NoVersionAvailableByUser as e:
        print("Cannot find solc version that meets both the requirement of "
              "the solidity file and the user requirement")
        print("Solidity file's requirement: ")
        print(e.sol_rule)
        print("User's requirement: ")
        print(e.user_rule)
    finally:
        return 1


if __name__ == '__main__':
    sys.exit(main())
