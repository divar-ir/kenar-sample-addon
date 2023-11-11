class DivarException(Exception):
    def __init__(
            self,
            message=None,
            *args
    ):
        self.message = message
        super(DivarException, self).__init__(message, *args)
