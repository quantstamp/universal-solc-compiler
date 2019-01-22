class NoVersionAvailableByUser(Exception):
    def __init__(self, available_versions, sol_rule, user_rule, msg):
        super(NoVersionAvailableByUser, self).__init__(msg)
        self.available_versions = available_versions
        self.sol_rule = sol_rule
        self.user_rule = user_rule
