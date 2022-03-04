class Stage_Manger:

    def __init__(self):
        self.states = []

    def processInput(self, event):
        for state in self.states:
            state.processInput(event)

    def update(self, dt):
        for state in self.states:
            state.update(dt)

    def render(self, surf):
        for state in self.states:
            state.render(surf)

    def set_state(self, state):
        if (len(self.states) > 0):
            self.states.pop()

        self.states.append(state)
        