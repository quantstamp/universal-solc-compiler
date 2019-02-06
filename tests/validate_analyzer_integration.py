####################################################################################################
#                                                                                                  #
# (c) 2019 Quantstamp, Inc. All rights reserved.  This content shall not be used, copied,          #
# modified, redistributed, or otherwise disseminated except to the extent expressly authorized by  #
# Quantstamp for credentialed users. This content and its use are governed by the Quantstamp       #
# Demonstration License Terms at <https://s3.amazonaws.com/qsp-protocol-license/LICENSE.txt>.      #
#                                                                                                  #
####################################################################################################


import subprocess
import filecmp
import pytest

"""
    This is not within the CI because it only checks the difference of uploaded docker images,
    Here we are comparing the output of mythril-0.4.25 and mythril-usolc-0.5.3
    
    to run the test, use the command below:
        `python -m pytest tests/validate_analyzer_integration.py` 
"""


@pytest.mark.parametrize("contract",[
    "DAOBug.sol",
    "DAOBug",
    "DAOBugOld-Caret.sol",
    "somefileThatDoesnotexist",
    "kyber",
    "Empty.sol",
])
def test_mythril(contract):
    """
    Test if the outputs of mythril-0.4.25 and mythril-usolc-0.5.3 are the same.
    """

    subprocess.run(["rm", "-rf", "/tmp/sol_test/compare_original"])
    subprocess.run(["rm", "-rf", "/tmp/sol_test/compare_usolc"])

    subprocess.run(["docker run --rm -v /tmp:/tmp -i qspprotocol/mythril-0.4.25 -o json -x "
                    "/tmp/sol_test/" + contract + " > /tmp/sol_test/compare_original"],
                   shell=True)

    subprocess.run(["docker run --rm -v /tmp:/tmp -i qspprotocol/mythril-usolc-0.5.3"
                    " -o json -x "
                    "/tmp/sol_test/" + contract + " > /tmp/sol_test/compare_usolc"],
                   shell=True)

    if not filecmp.cmp("/tmp/sol_test/compare_original", "/tmp/sol_test/compare_usolc"):
        original_report = open("/tmp/sol_test/compare_original", "r")
        new_report = open("/tmp/sol_test/compare_usolc", "r")

        for line in original_report:
            print(line)

        for line in new_report:
            print(line)

    assert(filecmp.cmp("/tmp/sol_test/compare_original", "/tmp/sol_test/compare_usolc") is True)


@pytest.mark.parametrize("contract",[
    "DAOBug.sol",
    "DAOBug",
    "DAOBugOld-Caret.sol",
    "somefileThatDoesnotexist",
    "kyber"
    "Empty.sol",
])
def test_securify(contract):
    """
    Test if the outputs of securify-0.4.25 and securify-usolc-0.5.3 are the same.
    """

    subprocess.run(["rm", "-rf", "/tmp/sol_test/compare_original"])
    subprocess.run(["rm", "-rf", "/tmp/sol_test/compare_usolc"])

    subprocess.run(["docker run --rm -v /tmp:/tmp -i qspprotocol/securify-0.4.25 -fs "
                    "/tmp/sol_test/" + contract + " > /tmp/sol_test/compare_original"],
                    shell=True)

    subprocess.run(["docker run --rm -v /tmp:/tmp -i qspprotocol/securify-usolc-0.5.3 -fs "
                    "/tmp/sol_test/" + contract + " > /tmp/sol_test/compare_usolc"],
                    shell=True)

    assert(filecmp.cmp("/tmp/sol_test/compare_original", "/tmp/sol_test/compare_usolc") is True)
