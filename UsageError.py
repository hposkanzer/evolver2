'''
Created on Aug 4, 2010

@author: hmp
'''

class UsageError(Exception):

    msg = ""
    
    def __init__(self, msg):
        self.msg = msg
        
    def __str__(self):
        return self.msg
    
    
