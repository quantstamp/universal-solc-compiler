class NoVersionAvailableBySol(Exception):
    def __init__(self, available_versions, sol_rule, msg):
        super(NoVersionAvailableBySol, self).__init__(msg)
        self.available_versions = available_versions
        self.sol_rule = sol_rule
