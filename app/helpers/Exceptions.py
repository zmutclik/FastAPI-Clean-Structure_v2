class RequiresLoginException(Exception):
    def __init__(self, nextRouter: str):
        self.nextRouter = nextRouter
