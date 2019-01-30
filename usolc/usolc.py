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
 solc ....... -U 0.4.*-          use oldest compiler in 0.4.*
 solc ....... -U +               use newest compiler available
 solc ....... -U -               use oldest compiler available

"""

import sys
import re
import subprocess
import semver
from enum import Enum
from exceptions.pragmaline_notfound_error import PragmaLineNotFoundError
from exceptions.noversion_available_by_sol import NoVersionAvailableBySol
from exceptions.noversion_available_by_user import NoVersionAvailableByUser


class VersionChoosing(Enum):
    NEWEST = 1
    OLDEST = 2


PRAGMA_SOLIDITY = re.compile(r'pragma\ssolidity\s(.*);', re.IGNORECASE)
additional_info = False


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


def extract_pragma_line(filename):
    """
    Opens the file, then find the line that indicates the solidity version
    Returns that line
    """
    pragma_line = None

    with open(filename, 'r') as file:
        for line in file:
            if PRAGMA_SOLIDITY.match(line) is not None:
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
    version_match = PRAGMA_SOLIDITY.search(line)
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
    global additional_info
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
        elif arg == "-uinfo":
            additional_info = True
        else:
            if arg[-4:] == ".sol":
                filename = arg
            native_argv.append(arg)

    version_selection_strategy = interpret_strategy_string(version_selection_strategy_str)

    return [filename, version_selection_strategy, native_argv]


def interpret_strategy_string(strategy_string):
    """
    Choosing strategy includes a user defined filter 
    and a preference to select the newest or oldest version possible

    This function reads the parameter string and interprets it with the following rule:

    [version filter](+-)

    semantic versioning can be used in the [version filter], 
    + indicates "prefer newest compiler", - indicates "prefer oldest compiler".

    if + or - is not indicated, then the default would be "prefer newest compiler"

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
        choosing = VersionChoosing.OLDEST
        version_filter = strategy_string[:-1]
    else:
        choosing = VersionChoosing.NEWEST
        version_filter = strategy_string

    return [version_filter, choosing]


def semver_min_satisfying(target_list, target_range):
    """
    Implementing the min_satisfying according to Node-Semver spec
    Obtaining the minimum/oldest version that satisfies target_range from the list
    """
    result_version = None
    user_filtered_list = semver_filter(target_list, target_range)

    for each_version in user_filtered_list:
        if result_version is None:
            result_version = each_version
        elif semver.gt(result_version, each_version, loose=True):
            result_version = each_version

    return result_version


def choose_version_by_strategy(target_list, version_selection_strategy):
    """
    Choose a specific version in the list, 
    according to version selection strategy specified by the user
    """
    
    [target_range, choosing] = version_selection_strategy

    if choosing == VersionChoosing.NEWEST:
        result = semver.max_satisfying(target_list, target_range, loose=True)
    else:
        # min_satisfying is not implemented by the library yet, using our own implementation
        result = semver_min_satisfying(target_list, target_range)

    return result


def choose_version_by_argument(available_versions, filename, version_selection_strategy):
    """
    Choose a specific version in the list by:
        (1) filtering it through the solidity requirement
        (2) filtering it through the user specification
        (3) Choose a version according to the user's preference
    """
    if filename is None:
        filtered_by_sol_compiler_list = available_versions
        sol_rule = ""
    else:
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
                "No solc version that satisfies both the requirement of" +
                " the solidity file and the user's rule")

    return version_chosen


def read_version_list(version_list_filename):
    """
    Opens the file and treat each line as a version available for solc
    """
    list_file = open(version_list_filename, "r")
    list_with_newline = list(list_file)
    nl_removed_list = [elem.rstrip('\n') for elem in list_with_newline]
    return list(nl_removed_list)


def run_solc(version_chosen, native_argv):
    if additional_info:
        print("solc version: " + version_chosen)
        print("#################################################")

    return subprocess.run(["/usr/local/bin/solc-versions/solc-"+version_chosen] + native_argv)


def main():
    valid_versions = read_version_list("/usr/local/bin/solc-versions/solc_version_list")

    try:
        [filename, version_selection_strategy, native_argv] = extract_arguments(sys.argv)

        if additional_info:
            print("#################################################")
            print("Available solc versions are: " + str(valid_versions))

        version_chosen = choose_version_by_argument(valid_versions, filename,
                                                    version_selection_strategy)
        run_solc(version_chosen, native_argv)
        return 0
    except PragmaLineNotFoundError:
        print("Cannot find pragma line that specifies version", file=sys.stderr)
        return 1
    except FileNotFoundError:
        print("Solidity file not found", file=sys.stderr)
        return 1
    except NoVersionAvailableBySol as e:
        print("Cannot find solc version that meets the requirement of the solidity file", file=sys.stderr)
        print("Solidity file's requirement: ", file=sys.stderr)
        print(e.sol_rule, file=sys.stderr)
        return 1
    except NoVersionAvailableByUser as e:
        print("Cannot find solc version that meets both the requirement of "
              "the solidity file and the user requirement", file=sys.stderr)
        print("Solidity file's requirement: ", file=sys.stderr)
        print(e.sol_rule, file=sys.stderr)
        print("User's requirement: ", file=sys.stderr)
        print(e.user_rule, file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
