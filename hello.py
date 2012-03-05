#!/usr/bin/env python
# coding=utf-8

import re
import web

def hello(phenny, input):
   phenny.say('Hello %s' % input.nick) 

def hodor(phenny, input):
   phenny.say('HODOR HODOR HODOR HODOR!')

hodor.commands = ['argh']
hodor.priority = 'low'
hello.commands = ['hello']
hello.priority = 'low'
