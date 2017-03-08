class Error(Exception):
    """Base class for exceptions in this module."""
    def __init__(self, message):
        self.message = message
        self.exit_code = 10

class FatalError(Error):
    """Error that should cause program to terminate"""
    def __init__(self, message):
        Error.__init__(self, message)
        self.fatal = True
        self.exit_code = 21

class WarningError(Error):
    """Error that should result in a Warning message"""
    def __init__(self, message):
        Error.__init__(self, message)
        self.fatal = False
        self.exit_code = 23

class InvalidResourceError(FatalError):
    """Exception indicating that user did not set a Resource Kind or set it Improperly"""
    def __init__(self, message):
        FatalError.__init__(self, message)
        self.exit_code = 31

class InvalidNamespaceError(FatalError):
    """Exception indicating that user did not set a Namespace or set it Improperly"""
    def __init__(self, message):
        FatalError.__init__(self, message)
        self.exit_code = 32

class InvalidEndpointError(FatalError):
    """Exception indicating that user did not set an API Endpoint or set it Improperly"""
    def __init__(self, message):
        FatalError.__init__(self, message)
        self.exit_code = 33

class InvalidTokenError(FatalError):
    """Exception indicating that user did not set a Token or set it Improperly"""
    def __init__(self, message):
        FatalError.__init__(self, message)
        self.exit_code = 34

class InsecureError(WarningError):
    """Exception indicating that user did not set a Resource Kind or set it Improperly"""
    def __init__(self, message):
        WarningError.__init__(self, message)
        self.exit_code = 40
