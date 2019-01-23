####################################################################################################
#                                                                                                  #
# (c) 2019 Quantstamp, Inc. All rights reserved.  This content shall not be used, copied,          #
# modified, redistributed, or otherwise disseminated except to the extent expressly authorized by  #
# Quantstamp for credentialed users. This content and its use are governed by the Quantstamp       #
# Demonstration License Terms at <https://s3.amazonaws.com/qsp-protocol-license/LICENSE.txt>.      #
#                                                                                                  #
####################################################################################################


class NoVersionAvailableByUser(Exception):
    def __init__(self, available_versions, sol_rule, user_rule, msg):
        super(NoVersionAvailableByUser, self).__init__(msg)
        self.available_versions = available_versions
        self.sol_rule = sol_rule
        self.user_rule = user_rule
