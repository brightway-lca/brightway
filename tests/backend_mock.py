class MockBackendConfig:
    def __init__(self):
        self.path = None

    def activate(self, dirpath):
        self.path = dirpath

    def deactivate(self):
        self.path = None


config = MockBackendConfig()
