# ferris-bot
A discord bot created with the sole purpose of handling polls for my server (and now other servers).

Examples:

Voting on two example polls:
[![Image from Gyazo](https://i.gyazo.com/145d9b8d01ec881cc02e45f49f48fdaa.gif)](https://gyazo.com/145d9b8d01ec881cc02e45f49f48fdaa)
Deleting a poll:
[![Image from Gyazo](https://i.gyazo.com/8f08c25cd809d0aa42aff327db87ca96.gif)](https://gyazo.com/8f08c25cd809d0aa42aff327db87ca96)

# Commands
## poll
    Creates a poll that users can vote on.
    Usage:
      $poll [title];[arg1];[arg2];[arg3];...
      [title] : the title or question of the poll
      [arg1]  : choice 1
      [arg2]  : choice 2
      [arg3]  : choice 3
      ...
    Example:
      $poll Should we go to the movies today?;Yes;No

  
## pollend
    Send a message to ask the author what polls they want to end.
    React to the message to select which poll to end and hit the thumbs up emoji to confirm.
    Usage:
      $pollend
    Example:
      Which poll would you like to end?
      1 Which movie for today?
      2 Who here is going bowling?

## respoll
    Create a reservation poll specifically for deciding which rpi dining hall to eat at.
    Usage:
      $respoll [type] [duration]
      [type]     : Breakfast, Lunch, Dinner
      [duration] : duration in minutes
    Example:
      $respoll dinner 30
    
## respollend
    End the current reservation poll.
    Can be used to end the reservation poll before the duration is up.
    Usage:
      $respollend

## quit
    Shuts down the bot.
    Usage: (must be an owner)
      $quit
