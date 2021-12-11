#!/usr/bin/env python3
import os, sys, io
import json
import config

class Logger:
    f      = None
    writer = None

    @classmethod
    def init(self):
        if Logger.writer:
            return
        try:
            os.remove(config.LOGFNAME)            
        except:
            pass
        if config.DEBUG:
            self.f      = io.FileIO(config.LOGFILENAME, 'w')
            self.writer = io.BufferedWriter(self.f)    

    
    @classmethod
    def logConsole(cls, s):
        if config.DEBUG:
            print(s)

    @classmethod
    def logFile(cls, s):
        if not cls.writer:
            cls.init()
        s+='\n'
        if cls.f!=None:
            cls.f.write(s.encode('utf-8'))

def LOGC(s):
    Logger.logConsole(s)

def LOGF(s):
    Logger.logFile(s)    

def LOG(s):
    Logger.logConsole(s)
    Logger.logFile(s)    

def LOGALWAYS(s):
    print(s)
    Logger.logFile(s)    
