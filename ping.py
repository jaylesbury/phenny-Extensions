#!/usr/bin/env python
"""
ping.py - Phenny Ping Module
Author: Sean B. Palmer, inamidst.com
About: http://inamidst.com/phenny/
"""

import random

def hello(phenny, input): 
   greeting = random.choice(('Hi', 'Hey', 'Hello'))
   punctuation = random.choice(('', '!'))
   phenny.say(greeting + ' ' + input.nick + punctuation)
hello.rule = r'(?i)(hi|hello|hey) $nickname[ \t]*$'

def interjection(phenny, input): 
   phenny.say(input.nick + '!')
interjection.rule = r'$nickname!'
interjection.priority = 'high'
interjection.thread = False

def thanks(phenny, input):
   phenny.say('No worries %s!' % input.nick)
thanks.rule = r'thanks,? $nickname.*'

def fuckyou(phenny, input):
   insult = random.choice(('dickhead', 'wanker', 'pillock', 'sorry love', 'your mother'))
   phenny.say(insult)
fuckyou.rule = r'fuck you $nickname.*'

def notaword(phenny, input):
   phenny.say(input.nick + ': not a word')
notaword.rule =r'.* vatch.*|vatch.*'

if __name__ == '__main__': 
   print __doc__.strip()
