
class State():
    def __init__(self):
        self.current_state = 'idle'

    def update(self, new_state = None):
        match self.current_state:
            case 'idle':
                if new_state:
                    self.current_state = new_state
            case 'ringing':
                self.current_state = 'talking'
            case 'talking':
                self.current_state = 'idle'
            case 'terminated':
                print("terminated")
            case _:
                print("unknown state")
