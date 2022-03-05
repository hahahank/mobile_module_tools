import os, re
import time
import sys
import argparse


DEFAULT_MAX_RETRY = 20
DEFAULT_TIMEOUT  = 3
DEFAULT_SUDO="ccs@123"
TEST_CMD =    [ 'AT+CGDCONT?',  'AT+CIMI' ]
RESTART_CMD = ['AT+CFUN=0',  'AT+CFUN=1'] 
RESET_CMD =   ['AT+CFUN=15'] 
MODULE={"Sierra"  : {
                     "CHECK":[	# -C
                          'AT+CGPADDR',
                          'AT!SELRAT?',
                          'AT+CIMI',
                          'AT+CGDCONT?',
                          'AT+COPS?',
                          'AT+CSQ',
                          #'AT+CESQ',
                          'AT!NRINFO?',
                     ],
                     "SET_N78":[	# -S 78
                          'AT!ENTERCND="A710"',
                          'AT!SELRAT=5',
                          'AT!RATCA=0,0,1',
                          'AT!BAND=0C',
                          'AT+CGDCONT=1,"IP","inventec.net"'
                     ],
                     "SET_N79":[	# -S 79
                          'AT!ENTERCND="A710"',
                          'AT!SELRAT=5',
                          'AT!RATCA=0,0,1',
                          'AT!BAND=0C',
                          'AT+CGDCONT=1,"IP","internet"'
                     ]
                    },
        "Fibocom" : {
                     "CHECK":[	# -C
                          "AT+GTSET?",
                          "AT+GTACT?",
                          "AT+GTAUTOCONNECT?",
                          'AT+CGDCONT?',
                          'AT+CIMI?',
                          'AT+COPS?',
                          'AT+CSQ',
                          'AT+CESQ',
                     ],
                     "SET_N78":[	# -S 78
                          'AT+GTSET="5GSACTR",1',
                          'AT+GTACT=14,,,5078',
                          'AT+CGDCONT=1,"IP","inventec.net"',
                          'AT+GTAUTOCONNECT=1',
                     ],
                     "SET_N79":[	# -S 79
                          'AT+GTSET="5GSACTR",1',
                          'AT+GTACT=14,,,5079',
                          'AT+CGDCONT=1,"IP","internet"',
                          'AT+GTAUTOCONNECT=1',
                     ]
                    }
       }


def checkRE(pats,txt):
    for pat in pats:
        txt = re.search(pat,str(txt))
        if(txt):
            txt = str(txt.group())
        else:
            txt = False
    return txt if txt else False
    
    
def send_at_by_mmcli(sudo_pw, timeout, max, modem, cmd):
    result=[]
    i = 0
    linux_cmd = "echo '{0}' | sudo -S timeout -s SIGKILL {1}s mmcli -m {2} --command='{3}'".format(sudo_pw, timeout, modem, cmd)
    while( not result and i < max):
        #time.sleep(0.5)
        result = os.popen(linux_cmd).readlines()
        i+=1
    result = "".join(result)
    #print(">> Execute Command :",cmd)      # DEBUG PRINT
    print(result)          # DEBUG PRINT
    return {"result":result}


def getModem():
    result = None
    txt = os.popen('mmcli -L').readlines()
    pats=["/org/freedesktop/ModemManager1/Modem/\d","/Modem/\d","\d"]
    result = checkRE(pats,txt)
    return result


def getModule():
    global MODULE
    result = None
    for module in MODULE.keys():
        r = os.popen('lsusb|grep {}'.format(module)).readlines()
        if r:
            result = module
    return result


def main():
    # python3 sendAT.py --passwd [SUDO PASSWORD]
    parser = argparse.ArgumentParser(description='Send AT Help')
    parser.add_argument("-p","--passwd",
                        nargs='?',      # 0 or 1
                        help="[PASSWD] sudo password",
                        default=DEFAULT_SUDO)
    parser.add_argument("-c",
                        "--commands",
                        nargs='+',      #  >1
                        help="[COMMANDs]")
    parser.add_argument("-M",
                        "--max",
                        nargs='?',      # 0 or 1
                        default=DEFAULT_MAX_RETRY,
                        type=int,
                        help="Max Retry times if AT command no response")
    parser.add_argument("-T",
                        "--timeout",
                        nargs='?',      # 0 or 1
                        default=DEFAULT_TIMEOUT,
                        type=int,
                        help="Set TIMEOUT if AT command no response")
    parser.add_argument("-e",
                        "--execute",
                        nargs='?', # 0 or 1 or 
                        help="[EXECUTE] TEST, CHECK, SET_N78, SET_N79, RESET, RESTART")
    parser.add_argument("-m",
                        "--modem",
                        nargs='?', # 0 or 1 or 
                        help="[EXECUTE] TEST, CHECK, SET_N78, SET_N79, RESET, RESTART",
                        type=int,
                        )
    args = parser.parse_args()
    sudo_pw = args.passwd
    timeout = args.timeout
    max     = args.max
    #print(args.modem)
    if(args.modem != None):
        modem = args.modem
    else:
    	modem = getModem()
        

    # Get commands
    if(args.execute):
        #print("Execute define command set ",args.execute)                   # DEBUG PRINT
        if(args.execute == "TEST"): 
            commands = TEST_CMD
        elif(args.execute == "RESTART"):
            commands = RESTART_CMD
        elif(args.execute == "RESET"):
            commands = RESET_CMD
        else:
            module  = getModule()
            commands = MODULE.get(module)[args.execute]
    elif(args.execute == None and args.commands):
        commands = args.commands
    else:
        print("No test and No command",args.execute)
        commands=[]
    # Execute Commands
    for cmd in commands:
        #time.sleep(0.5)
        send_at_by_mmcli(sudo_pw, timeout, max, modem, cmd)

if __name__ == "__main__":
    main()
