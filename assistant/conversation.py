# ============================================================
# Conversation state
# ============================================================

class ConversationState:
    """
    Store the state of an active conversational flow.
    """

    def __init__(self):
        self.reset()

    def reset(self):
        """
        Reset the conversation to an inactive state.
        """

        self.active = False
        self.flow = None
        self.step = None
        self.data = {}

    def start(self, flow):
        """
        Start a new conversational flow.
        """

        self.active = True
        self.flow = flow
        self.step = None
        self.data = {}

    def end(self):
        """
        End the current conversational flow.
        """

        self.reset()