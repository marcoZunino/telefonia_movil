
class State():
    def __init__(self):
        self.current_state = 'idle'
        self.last_data = None
        self.dest_user_info = None

    def update(self, new_state = None):
        self.current_state = new_state
    
    def save_data(self, data):
        self.last_data = data

    def save_dest_user_info(self, data):
        self.dest_user_info = data

    def reset(self):
        self.current_state = 'idle'
        self.last_data = None
        self.dest_user_info = None


