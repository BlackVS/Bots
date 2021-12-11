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



class LoggerFile:
    f      = None
    writer = None

    def __init__(self, fname=None):
        if not fname:
            return
        try:
            os.remove(fname)            
        except:
            pass
        if config.DEBUG:
            self.f      = io.FileIO(fname, 'w')
            self.writer = io.BufferedWriter(self.f)    

    
    def log(self, s, endl='\n'):
        if self.writer:
            s+=endl
            if self.f!=None:
                self.f.write(s.encode('utf-8'))

    def log_object(self, obj, logtypes=True):
        if not self.writer or self.f==None:
            return
        vs = vars(obj)

        if logtypes:
            vs1 = " ".join( "{}={}".format(k, type(v).__name__ ) for k,v in vs.items())
            vs1+="\n"
            self.f.write(vs1.encode('utf-8'))

        vs2 = " ".join( "{}={}".format(k, v) for k,v in vs.items() if type(v) in (int, str, bool, type(None)) ) #only simple types
        vs2+="\n"
        self.f.write(vs2.encode('utf-8'))

    def log_types(self, obj):
        if not self.writer or self.f==None:
            return
        vs = vars(obj)
        vs1 = " ".join( "{}={}".format(k, type(v).__name__ ) for k,v in vs.items())
        vs1+="\n"
        self.f.write(vs1.encode('utf-8'))

    def log_info(self, s):
        self.log("INFO: "+s)