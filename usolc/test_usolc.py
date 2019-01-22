####################################################################################################
#                                                                                                  #
# (c) 2019 Quantstamp, Inc. All rights reserved.  This content shall not be used, copied,          #
# modified, redistributed, or otherwise disseminated except to the extent expressly authorized by  #
# Quantstamp for credentialed users. This content and its use are governed by the Quantstamp       #
# Demonstration License Terms at <https://s3.amazonaws.com/qsp-protocol-license/LICENSE.txt>.      #
#                                                                                                  #
####################################################################################################


from usolc.usolc import *
import pytest

@pytest.fixture
def sample_version_list():
    return ["0.3.9", "0.4.1", "0.4.2", "0.4.3", "0.5.0", "1.0.0", "1.0.1"]


@pytest.mark.parametrize(   "rule_text,expected_result", [
    ("^0.4.2", ["0.4.2", "0.4.3"]),
])
def test_semver_filter(sample_version_list, rule_text, expected_result):
    """ Test semver_filter """
    result = list(semver_filter(sample_version_list, rule_text))
    assert(result == expected_result)


@pytest.mark.parametrize("filename,expected_line",[
    ("resources/exactly_one.sol","pragma solidity 0.4.18;\n"),
    ("resources/caret.sol","pragma solidity ^0.4.18;\n"),
    ("resources/range.sol","pragma solidity >=0.4.22 <0.6.0;\n"),
    ("resources/range_or_one.sol","pragma solidity 0.4.21 || >=0.4.25 <0.6.0;\n"),       
])
def test_extract_pragma_line(filename,expected_line):
    """ Test extract_pragma_line for cases that there both the file and the pragma line exist """
    extracted_line = extract_pragma_line(filename)
    assert(expected_line == extracted_line) 


def test_extract_pragma_line_throws_pragmanotfound():
    """
    Test extract_pragma_line throws PragmaLineNotFoundError
    when the file exists but the line doesn't
    """
    with pytest.raises(PragmaLineNotFoundError):
        extract_pragma_line("resources/empty.sol")


def test_extract_pragma_line_throws_file_not_found():
    """ Test extract_pragma_line throws exception FileNotFoundError when the file doesn't exist """
    with pytest.raises(FileNotFoundError):
        extract_pragma_line("from_somerandomfilenamethat_shouldnt_exist.sol")


@pytest.mark.parametrize("pragma, expected_rule",[
    ("pragma solidity 0.4.18;\n", "0.4.18"),
    ("pragma solidity ^0.4.18;\n","^0.4.18"),
    ("pragma solidity >=0.4.22 <0.6.0;\n",">=0.4.22 <0.6.0"),
    ("pragma solidity 0.4.21 || >=0.4.25 <0.6.0;\n","0.4.21 || >=0.4.25 <0.6.0"),       
])
def test_getrule_from_pragma(pragma, expected_rule):
    """ Test getrule_from_pragma """
    extracted_rule = getrule_from_pragma(pragma)
    assert(expected_rule == extracted_rule) 


@pytest.mark.parametrize("filename,expected_rule",[
    ("resources/exactly_one.sol","0.4.18"),
    ("resources/caret.sol","^0.4.18"),
    ("resources/range.sol",">=0.4.22 <0.6.0"),
    ("resources/range_or_one.sol","0.4.21 || >=0.4.25 <0.6.0"),       
])
def test_getrule_from_file(filename,expected_rule):
    """ Test getrule_from_fiole """
    extracted_rule = getrule_from_file(filename)
    assert(expected_rule == extracted_rule) 



@pytest.mark.parametrize("sys_argv, expected_result",[
    (["solc","hello.sol", "-U", "0.4.2+" , "--abi", "hello"],
     ["hello.sol", ["0.4.2", VersionChoosing.NEWEST], ["hello.sol","--abi", "hello"]]),

    (["solc","hello.sol", "-U", "0.4.2+" , "--abi"],
     ["hello.sol", ["0.4.2", VersionChoosing.NEWEST],["hello.sol","--abi"]]),

    (["solc","hello.sol", "--abi"],
     ["hello.sol", ["*",VersionChoosing.NEWEST], ["hello.sol","--abi"]]),

    (["solc","hello.sol"],
     ["hello.sol", ["*",VersionChoosing.NEWEST], ["hello.sol"]]),
])
def test_extract_arguments(sys_argv, expected_result):
    """ Test extract_arguments when .sol is found in the parameters"""
    extracted_result = extract_arguments(sys_argv)
    assert(expected_result == extracted_result)   


def test_extract_arguments_throw_filename_not_found_in_argument():
    """ Test extract_arguments throws FilenameNotFoundInArgument when .sol is not found """
    with pytest.raises(FilenameNotFoundInArgument):
        extract_arguments(["solc", "--abi"])


@pytest.mark.parametrize("strategy_string, expected_result",[
    ("^0.4.1+", ["^0.4.1", VersionChoosing.NEWEST]),
    (">=0.4.1 <0.4.23", [">=0.4.1 <0.4.23", VersionChoosing.NEWEST]),
    (">=0.4.1 <0.4.23+", [">=0.4.1 <0.4.23", VersionChoosing.NEWEST]),
    (">=0.4.1 <0.4.23-", [">=0.4.1 <0.4.23", VersionChoosing.OLDEST]),
    (">=0.4.5 <0.4.23 || 0.4.3-", [">=0.4.5 <0.4.23 || 0.4.3", VersionChoosing.OLDEST]),
])
def test_interpret_strategy_string(strategy_string, expected_result):
    """ Test interpret_strategy_string """
    extracted_result = interpret_strategy_string(strategy_string)
    assert(extracted_result == expected_result)


# choose_version_by_strategy
@pytest.mark.parametrize("version_selection_strategy, expected_version",[
    (["^0.4.1", VersionChoosing.NEWEST],"0.4.3"),
])
def test_choose_version_by_strategy(sample_version_list,
                                    version_selection_strategy, expected_version):
    """ Test choose_version_by_strategy """
    result_version = choose_version_by_strategy(sample_version_list, version_selection_strategy)
    assert(result_version == expected_version)

