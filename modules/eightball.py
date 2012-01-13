from random import randint

_responses = ['It is possible.', 'Yes!', 'Of course.',
                           'Naturally.', 'Obviously.', 'It shall be.',
                           'The outlook is good.', 'It is so.',
                           'One would be wise to think so.',
                           'The answer is certainly yes.',
              'In your dreams.', 'I doubt it very much.',
                           'No chance.', 'The outlook is poor.',
                           'Unlikely.', 'About as likely as pigs flying.',
                           'You\'re kidding, right?', 'NO!', 'NO.', 'No.',
                           'The answer is a resounding no.',
              'Maybe...', 'No clue.', '_I_ don\'t know.',
                           'The outlook is hazy, please ask again later.',
                           'What are you asking me for?', 'Come again?',
                           'You know the answer better than I.',
                           'The answer is def-- oooh! shiny thing!']

def eightball(bot,*args):
    """Decide your fate"""
    bot.reply(_responses[randint(0,len(_responses) - 1)])
eightball.commands = ['eightball']
