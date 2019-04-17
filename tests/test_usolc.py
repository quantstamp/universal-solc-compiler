####################################################################################################
#                                                                                                  #
# (c) 2019 Quantstamp, Inc. All rights reserved.  This content shall not be used, copied,          #
# modified, redistributed, or otherwise disseminated except to the extent expressly authorized by  #
# Quantstamp for credentialed users. This content and its use are governed by the Quantstamp       #
# Demonstration License Terms at <https://s3.amazonaws.com/qsp-protocol-license/LICENSE.txt>.      #
#                                                                                                  #
####################################################################################################


from usolc.usolc import *
from solc import compile_standard
import pytest



@pytest.fixture
def sample_version_list():
    return ["0.3.9", "0.4.1", "0.4.2", "0.4.3", "0.4.18", "0.5.0", "1.0.0", "1.0.1"]


@pytest.mark.parametrize("rule_text,expected_result", [
    ("^0.4.2", ["0.4.2", "0.4.3", "0.4.18"]),
])
def test_semver_filter(sample_version_list, rule_text, expected_result):
    """ Test semver_filter """
    result = list(semver_filter(sample_version_list, rule_text))
    assert(result == expected_result)


@pytest.mark.parametrize("filename,expected_line", [
    ("exactly_one.sol", "pragma solidity 0.4.18;\n"),
    ("caret_0.4.sol", "pragma solidity ^0.4.18;\n"),
    ("range.sol", "pragma solidity >=0.4.22 <0.6.0;\n"),
    ("range_or_one.sol", "pragma solidity 0.4.21 || >=0.4.25 <0.6.0;\n"),
])
def test_extract_pragma_line(filename, expected_line):
    """ Test extract_pragma_line for cases that there both the file and the pragma line exist """
    extracted_line = extract_pragma_line("resources/"+filename)
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


@pytest.mark.parametrize("pragma, expected_rule", [
    ("pragma solidity 0.4.18;\n", "0.4.18"),
    ("pragma solidity ^0.4.18;\n", "^0.4.18"),
    ("pragma solidity >=0.4.22 <0.6.0;\n", ">=0.4.22 <0.6.0"),
    ("pragma solidity 0.4.21 || >=0.4.25 <0.6.0;\n", "0.4.21 || >=0.4.25 <0.6.0"),
])
def test_getrule_from_pragma(pragma, expected_rule):
    """ Test getrule_from_pragma """
    extracted_rule = getrule_from_pragma(pragma)
    assert(expected_rule == extracted_rule) 


@pytest.mark.parametrize("filename,expected_rule", [
    ("resources/exactly_one.sol", "0.4.18"),
    ("resources/caret_0.4.sol", "^0.4.18"),
    ("resources/range.sol", ">=0.4.22 <0.6.0"),
    ("resources/range_or_one.sol", "0.4.21 || >=0.4.25 <0.6.0"),
    ("resources/empty.sol", "*"),
])
def test_getrule_from_file(filename, expected_rule):
    """ Test getrule_from_fiole """
    extracted_rule = getrule_from_file(filename)
    assert(expected_rule == extracted_rule) 


@pytest.mark.parametrize("sys_argv, expected_result", [
    (["solc", "hello.sol", "-U", "0.4.2+", "--abi", "extrarandom", "-uinfo"],
     ["hello.sol", ["0.4.2", VersionChoosing.NEWEST], ["hello.sol", "--abi", "extrarandom"]]),

    (["solc", "hello.sol", "-U", "0.4.2+", "--abi"],
     ["hello.sol", ["0.4.2", VersionChoosing.NEWEST], ["hello.sol", "--abi"]]),

    (["solc", "hello.sol", "--abi"],
     ["hello.sol", ["*", VersionChoosing.NEWEST], ["hello.sol", "--abi"]]),

    (["solc", "hello.sol"],
     ["hello.sol", ["*", VersionChoosing.NEWEST], ["hello.sol"]]),

    (["solc", "this_is_solfile_without_sol_end"],
     ["this_is_solfile_without_sol_end", ["*", VersionChoosing.NEWEST], ["this_is_solfile_without_sol_end"]]),

    (["solc", "first_sol", "second_sol"],
     ["first_sol", ["*", VersionChoosing.NEWEST], ["first_sol", "second_sol"]]),

    (["solc", "path=declaration", "this_is_solfile_without_sol_end", "--abi"],
     ["this_is_solfile_without_sol_end", ["*", VersionChoosing.NEWEST],
      ["path=declaration", "this_is_solfile_without_sol_end", "--abi"]]),

    (["solc", "path=declaration", "this_is_solfile_without_sol_end_1", "--combined-json=asm,abi",
      "this_is_solfile_without_sol_end_2", "--abi"],
     ["this_is_solfile_without_sol_end_1", ["*", VersionChoosing.NEWEST],
      ["path=declaration", "this_is_solfile_without_sol_end_1", "--combined-json=asm,abi",
       "this_is_solfile_without_sol_end_2", "--abi"]]),

    (["solc", "path=declaration", "this_is_solfile_without_sol_end_1", "--combined-json", "asm,abi",
      "this_is_solfile_without_sol_end_2", "--abi"],
     ["this_is_solfile_without_sol_end_1", ["*", VersionChoosing.NEWEST],
      ["path=declaration", "this_is_solfile_without_sol_end_1", "--combined-json", "asm,abi",
       "this_is_solfile_without_sol_end_2", "--abi"]]),

    (["solc", "--version"],
     [None, ["*", VersionChoosing.NEWEST], ["--version"]]),
])
def test_extract_arguments(sys_argv, expected_result):
    """ Test extract_arguments when .sol is found in the parameters"""
    extracted_result = extract_arguments(sys_argv)
    assert(expected_result == extracted_result)   


@pytest.mark.parametrize("strategy_string, expected_result", [
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


@pytest.mark.parametrize("version_list, expected_version", [
    (["0.3.9", "0.4.1", "0.4.2", "0.4.3", "0.4.18", "0.5.0", "1.0.0", "1.0.1"], "0.3.9"),
    (["1.0.1", "0.4.1", "0.3.9", "0.4.2", "0.4.3", "0.4.18", "0.5.0", "1.0.0"],  "0.3.9"),
])
def test_semver_min_satisfying_normal(version_list, expected_version):
    """ Test semver_min_satisfying when there should be a result_version """
    result_version = semver_min_satisfying(version_list, "*")
    assert(result_version == expected_version)


def test_semver_min_satisfying_none(sample_version_list):
    """ Test semver_min_satisfying when result_version should be None """
    result_version = semver_min_satisfying(sample_version_list, ">5.0.0")
    assert(result_version is None)


@pytest.mark.parametrize("version_selection_strategy, expected_version", [
    (["^0.4.1", VersionChoosing.NEWEST], "0.4.18"),
    (["^0.4.1", VersionChoosing.OLDEST], "0.4.1"),
])
def test_choose_version_by_strategy(sample_version_list,
                                    version_selection_strategy, expected_version):
    """ Test choose_version_by_strategy """
    result_version = choose_version_by_strategy(sample_version_list, version_selection_strategy)
    assert(result_version == expected_version)


@pytest.mark.parametrize("filename, version_selection_strategy, expected_version", [
    ("exactly_one.sol", ["^0.4.1", VersionChoosing.NEWEST], "0.4.18"),
    ("caret_0.4.sol", ["0.4.18", VersionChoosing.NEWEST], "0.4.18"),
    ("range.sol", ["*", VersionChoosing.NEWEST], "0.5.0"),
    ("range_or_one.sol", ["*", VersionChoosing.NEWEST], "0.5.0"),
    (None, ["*", VersionChoosing.NEWEST], "1.0.1"),
])
def test_choose_version_by_argument_normal(sample_version_list,
                                           filename, version_selection_strategy, expected_version):
    """ Test choose_version_by_argument when all arguments are properly given """

    if filename is None:
        filelocation = None
    else:
        filelocation = "resources/" + filename

    result_version = \
        choose_version_by_argument(sample_version_list, filelocation, version_selection_strategy)
    assert(expected_version == result_version)


def test_choose_version_by_argument_throws_no_version_available_by_sol():
    """
    Test choose_version_by_argument
    when rule from solidity ruled out all available solutions,
    it should throw NoVersionAvailableBySol
    """
    with pytest.raises(NoVersionAvailableBySol):
        choose_version_by_argument(["0.3.9"], "resources/exactly_one.sol", ["*", VersionChoosing.NEWEST])


def test_choose_version_by_argument_throws_no_version_available_by_user():
    """
    Test choose_version_by_argument when rule from solidity
    when rule specified by the user ruled out all available solutions,
    it should throw NoVersionAvailableByUser
    """
    with pytest.raises(NoVersionAvailableByUser):
        choose_version_by_argument(["0.4.18"],
                                   "resources/exactly_one.sol", ["^0.4.19", VersionChoosing.NEWEST])


def test_read_version_list():
    """
    Test read_version_list to see if it properly reads the versions provided in the file,
    The versions should not include special characters like \n or \r
    """
    extracted_list = read_version_list("usolc/solc_version_list")
    expected_list = ["0.5.4", "0.5.3", "0.5.2", "0.5.1", "0.5.0", "0.4.25", "0.4.24", "0.4.23",
                     "0.4.22", "0.4.21", "0.4.20", "0.4.19", "0.4.18", "0.4.17", "0.4.16",
                     "0.4.15", "0.4.14", "0.4.13", "0.4.12", "0.4.11", "0.4.10", "0.4.9",
                     "0.4.8", "0.4.7", "0.4.6", "0.4.5"]
    assert(expected_list == extracted_list)


def test_run_solc():
    """
    Test run_solc, passing normal arguments to see if it properly runs without failure
    """
    version_chosen = "0.4.25"
    native_argv = ["resources/caret_0.4.sol", "--abi"]
    process_return = run_solc(version_chosen, native_argv)
    assert(process_return.returncode == 0)


@pytest.mark.parametrize("sys_argv, expected_bin_file", [
    (["solc", "resources/caret_0.4.sol", "--bin", "-o", "test_bin_1", "-U", "0.4.25", "-uinfo"],
     "resources/caret_0.4.25.bin"),
    (["solc", "resources/caret_0.5.sol", "--bin", "-o", "test_bin_2", "-U", "0.5.0"],
     "resources/caret_0.5.0.bin"),
    (["solc", "resources/caret_0.5", "--bin", "-o", "test_bin_3", "-U", "0.5.3", "-uinfo"],
     "resources/caret_0.5_nosol.bin"),
])
def test_main(sys_argv, expected_bin_file):
    """
    Test main and compile a solidity file for 0.4.25 and another for 0.5.0, compare them with
    the bin file we expected.
    """
    sys.argv = sys_argv
    assert(main() == 0)
    expected_bin_file = [elem.rstrip('\n') for elem in list(open(expected_bin_file, "r"))]
    produced_bin_file = list(open((sys_argv[4] + "/Ballot.bin"), "r"))
    assert(expected_bin_file == produced_bin_file)


@pytest.mark.parametrize("sys_argv", [
    (["solc", "some_random_file_should_not_exist.sol", "--bin", "-o", "test_bin", "-U", "0.5.0"]),
    (["solc", "resources/exactly_0.6.0.sol", "--bin", "-o", "test_bin"]),
    (["solc", "resources/caret_0.5.sol", "--bin", "-o", "test_bin", "-U", "0.4.25"]),
])
def test_main_exception_return_1(sys_argv):
    """
    Test if main returns 1 when there is an exception being raised.
    The test cases is going through all exceptions that is being listed in the main()
    """
    sys.argv = sys_argv
    assert(main() == 1)


def test_solc_compile_standard():
    compile_standard({
            'language': 'Solidity',
            'sources': {
                'flattenedContract.sol': {'content': {"content":"pragma solidity ^0.4.24;\n/**\n* @title SafeMath\n*/\nlibrary SafeMath {\nfunction mul(uint256 a, uint256 b) internal pure returns (uint256) {\nif (a == 0) {\nreturn 0;\n}\nuint256 c = a * b;\nassert(c / a == b);\nreturn c;\n}\nfunction div(uint256 a, uint256 b) internal pure returns (uint256) {\n// assert(b > 0); // Solidity automatically throws when dividing by 0\nuint256 c = a / b;\n// assert(a == b * c + a % b); // There is no case in which this doesn't hold\nreturn c;\n}\nfunction sub(uint256 a, uint256 b) internal pure returns (uint256) {\nassert(b <= a);\nreturn a - b;\n}\nfunction add(uint256 a, uint256 b) internal pure returns (uint256) {\nuint256 c = a + b;\nassert(c >= a);\nreturn c;\n}\n}\n/**\n* @title Ownable\n*/\ncontract Ownable {\naddress public owner;\nevent OwnershipTransferred(address indexed previousOwner, address indexed newOwner);\nconstructor() public {\nowner = 0x266E16Ae64C9baC3A175235500Cc2cb1FF61d460;\n}\nmodifier onlyOwner() {\nrequire(msg.sender == owner);\n_;\n}\nfunction transferOwnership(address newOwner) public onlyOwner {\nrequire(newOwner != address(0));\nemit OwnershipTransferred(owner, newOwner);\nowner = newOwner;\n}\n}\n/**\n* @title ERC20Basic\n*/\ncontract ERC20Basic {\nfunction totalSupply() public view returns (uint256);\nfunction balanceOf(address who) public view returns (uint256);\nfunction transfer(address to, uint256 value) public returns (bool);\nevent Transfer(address indexed from, address indexed to, uint256 value);\n}\n/**\n* @title ERC20 interface\n*/\ncontract ERC20 is ERC20Basic {\nfunction allowance(address owner, address spender) public view returns (uint256);\nfunction transferFrom(address from, address to, uint256 value) public returns (bool);\nfunction approve(address spender, uint256 value) public returns (bool);\nevent Approval(address indexed owner, address indexed spender, uint256 value);\n}\n/**\n* @title Basic token\n*/\ncontract BasicToken is ERC20Basic {\nusing SafeMath for uint256;\nmapping(address => uint256) balances;\nuint256 totalSupply_;\nfunction totalSupply() public view returns (uint256) {\nreturn totalSupply_;\n}\nfunction transfer(address _to, uint256 _value) public returns (bool) {\nrequire(_to != address(0));\nrequire(_value <= balances[msg.sender]);\nbalances[msg.sender] = balances[msg.sender].sub(_value);\nbalances[_to] = balances[_to].add(_value);\nemit Transfer(msg.sender, _to, _value);\nreturn true;\n}\nfunction balanceOf(address _owner) public view returns (uint256 balance) {\nreturn balances[_owner];\n}\n}\n/**\n* @title Standard ERC20 token\n*/\ncontract StandardToken is ERC20, BasicToken {\nmapping (address => mapping (address => uint256)) internal allowed;\nfunction transferFrom(address _from, address _to, uint256 _value) public returns (bool) {\nrequire(_to != address(0));\nrequire(_value <= balances[_from]);\nrequire(_value <= allowed[_from][msg.sender]);\nbalances[_from] = balances[_from].sub(_value);\nbalances[_to] = balances[_to].add(_value);\nallowed[_from][msg.sender] = allowed[_from][msg.sender].sub(_value);\nemit Transfer(_from, _to, _value);\nreturn true;\n}\nfunction approve(address _spender, uint256 _value) public returns (bool) {\nallowed[msg.sender][_spender] = _value;\nemit Approval(msg.sender, _spender, _value);\nreturn true;\n}\nfunction allowance(address _owner, address _spender) public view returns (uint256) {\nreturn allowed[_owner][_spender];\n}\nfunction increaseApproval(address _spender, uint _addedValue) public returns (bool) {\nallowed[msg.sender][_spender] = allowed[msg.sender][_spender].add(_addedValue);\nemit Approval(msg.sender, _spender, allowed[msg.sender][_spender]);\nreturn true;\n}\nfunction decreaseApproval(address _spender, uint _subtractedValue) public returns (bool) {\nuint oldValue = allowed[msg.sender][_spender];\nif (_subtractedValue > oldValue) {\nallowed[msg.sender][_spender] = 0;\n} else {\nallowed[msg.sender][_spender] = oldValue.sub(_subtractedValue);\n}\nemit Approval(msg.sender, _spender, allowed[msg.sender][_spender]);\nreturn true;\n}\n}\ncontract eXdoradoTrade is StandardToken, Ownable {\n\nstring public name;\nstring public symbol;\nuint8 public decimals;\nuint256 public initialSupply;\nconstructor() public {\nname = 'eXdorado Trade';\nsymbol = 'EXT';\ndecimals = 18;\ninitialSupply = 100000000 * 10 ** uint256(decimals);\ntotalSupply_ = initialSupply;\nbalances[owner] = initialSupply;\nemit Transfer(0x0, owner, initialSupply);\n}\n}"}
            }
        })
