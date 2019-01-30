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


def test_mythril():
    """
    Test if the outputs of mythril-0.4.25 and mythril-usolc-0.5.3 are the same.
    """

    # Empty.sol will fail for mythril-0.4.25, seems like solc 0.4.25 couldn't handle empty file
    contracts = ["DAOBug", "DAOBugOld-Caret", "kyber"]

    for contract in contracts:
        subprocess.run(["rm", "-rf", "/tmp/sol_test/compare_original"])
        subprocess.run(["rm", "-rf", "/tmp/sol_test/compare_usolc"])

        subprocess.run(["docker run --rm -v /tmp:/tmp -i qspprotocol/mythril-0.4.25 -o json -x "
                       "/tmp/sol_test/" + contract + ".sol > /tmp/sol_test/compare_original"],
                       shell=True)

        subprocess.run(["docker run --rm -v /tmp:/tmp -i qspprotocol/mythril-usolc-0.5.3 -o json -x "
                       "/tmp/sol_test/" + contract + ".sol > /tmp/sol_test/compare_usolc"],
                       shell=True)

        assert(filecmp.cmp("/tmp/sol_test/compare_original", "/tmp/sol_test/compare_usolc") is True)


