
class State():
    def __init__(self):
        self.current_state = 'idle'
        self.last_data = None

    def update(self, new_state = None):
        self.current_state = new_state
    
    def save_data(self, data):
        self.last_data = data