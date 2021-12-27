class dining_hall_data:
  def __init__(self):
    '''
    A class to hold information for a poll specifically for
    deciding which rpi dining hall to eat at.
    '''
    self.is_active = False
    self.type = None
    self.times = None
    self.msg = None
    self.emoji_list = None
    self.creation_time = None
    self.reactions = None

  def activate(self, type):
    '''
    Takes type (Breakfast, Lunch, or Dinner) and "activates" the poll if
    the type is valid. The other info is added later after the message is created.
    Returns True if type is valid. 
    '''
    if (type.lower() in map(lambda str: str.lower(), self.all_times.keys())):
      self.is_active = True
      self.type = type.lower().title()
      self.times = self.all_times[self.type] # A list of times for the selected type.
      return True
    else:
      return False

  def add_info(self, msg, creation_time, emoji_list):
    '''
    After the message is created, additional info is added through this function.
    Returns nothing.
    '''
    self.msg = msg
    self.creation_time = creation_time
    self.emoji_list = emoji_list # A list of all the emojis that will be used as reactions
    self.reactions = dict()
    for i in range(len(self.times)):
      # Adds the number emojis to emoji_list
        self.emoji_list.append('{}️⃣'.format(i+1))
    for emoji in self.emoji_list:
      # Creates the reaction dictionary where the keys are the emojis
      # and the item would be a list of people who reacted with that emoji.
      self.reactions[emoji] = []

  def add_emojis_to_text(self, text):
    '''
    Takes the text and adds each emoji with the number of reservations and who reacted.
    Example where E is an emoji:
      E : 2 (@Person1, @Person2)
    Returns the modified text to be edited onto the message.
    '''
    for i in range(len(self.halls)): 
      # For each dining hall add the count and people who reacted to it. 
      text += '{} {} : {} ({})\n'.format( self.emoji_list[i], \
                                          self.halls[i], \
                                          len(self.reactions[self.emoji_list[i]]), \
                                          " ".join(self.reactions[self.emoji_list[i]]) )
    for i in range(len(self.times)):
      # For each time add the count and people who reacted to it. 
      text += '{} {} : {} ({})\n'.format( self.emoji_list[i+len(self.halls)], \
                                          self.times[i], \
                                          len(self.reactions[self.emoji_list[i+len(self.halls)]]), \
                                          " ".join(self.reactions[self.emoji_list[i+len(self.halls)]]) )
    text += f'\nPoll closes at **{self.creation_time[3]:02}:{self.creation_time[4]:02}**'
    return text

  # -----=== Const Variables ===-----
  halls = [ 'Barh', 'Blitman', 'Commons', 'Sage', 'Moes', 'None', 'Dont_Care' ]
  all_times = { 'Breakfast':['8:00', '8:30', '9:00', '9:30'], \
                'Lunch':['11:30', '12:00', '12:30', '1:00', '1:30', '2:00'], \
                'Dinner':['5:30', '6:00', '6:30', '7:00'] }