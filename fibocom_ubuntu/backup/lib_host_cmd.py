
from comm import *        # agent use this
#from .comm import *      # web use this
import re, os , json
import logging
from  time import sleep
import paramiko

def checkRE(pats,txt):
    for pat in pats:
        txt = re.search(pat,str(txt))
        if(txt):
            txt = str(txt.group())
        else:
            txt = False
    return txt if txt else False

def run(cmd):
    result = os.popen(cmd).readlines()
    result = "".join(result)
    return result

# RUN AT COMMAND
def run_at_without_check(cmd):
    my_cmd = 'timeout 30 python3 {}{} --passwd {} --timeout 4  -M 15 -c "{}"'.format(API_PATH,AT_API_FILE,HOST_PASSWORD, cmd )
    result = run(my_cmd)
    return result
 
def run_at_with_check(cmd,pats):
    my_cmd = 'timeout 30 python3 {}{} --passwd {} --timeout 4  -M 15 -c "{}"'.format(API_PATH,AT_API_FILE,HOST_PASSWORD, cmd )
    txt = run(cmd)
    result = checkRE(pats,txt)
 #   b = "** Check Result " + str(result)
 #   print(b)    # DEBUG
    return result


##
## Main / Test
##

if __name__ == '__main__' :
     run_at_with_check
