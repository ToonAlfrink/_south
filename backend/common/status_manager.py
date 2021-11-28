class _StatusManager:
    def __init__(self):
        self.states = dict()
        self.is_ready = True

    def ready(self): return self.is_ready

    def set_state(self, key, value):
        self.states[key] = value
        self.is_ready = len(self.states) == 0 or all(self.states.values())

    def get_state(self, key):
        return self.states[key]


status_manager = _StatusManager()
