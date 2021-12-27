class poll_data:
  """
  A simple class for holding a poll's information.
  """
  def __init__(self, msg_, reactions_, items_):
    self.msg = msg_
    self.reactions = reactions_
    self.items = items_
  def return_all_var(self):
    return self.msg, self.reactions, self.items
