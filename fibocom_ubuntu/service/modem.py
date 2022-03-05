import re, os
import logging
from statistics import mode
from  time import sleep
import paramiko
## LOG SETTING
import logging
import datetime
BASE_DIR = "/opt/fibocom_ubuntu/service/"
log_path = BASE_DIR + "/log/"
log_filename = log_path + datetime.datetime.now().strftime("%Y-%m-%d.log")#_%H_%M_%S
 
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
	'[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s',
	datefmt='%Y%m%d %H:%M:%S')

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)

fh = logging.FileHandler(log_filename)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

logger.addHandler(ch)
logger.addHandler(fh)
## END LOG SETTING
API_PATH = BASE_DIR     
AT_API_FILE = "sendAT.py"               
HOST_PASSWORD="aaa"
FIBOCOM= "Fibocom"
SIERRA = "Sierra"
MMCLI_TIMEOUT = 4
MMCLI_MAX_TRY = 15
SENT_AT_TIMEOUT = 30

MODULE=[SIERRA,FIBOCOM]
def checkRE(pats,txt):
    
    for pat in pats:
        #print("pat:",pat,"   txt:",txt)
        txt = re.search(pat,str(txt))
        if(txt):
            txt = str(txt.group())
        else:
            txt = False
    return txt if txt else False

def run(modem, at_cmd="",pats=[]):
    result=""
    if(at_cmd):
        linux_cmd = "timeout {at_timeout} python3 {path}{file} --passwd {pw} --timeout {mmcli_timeout} -m {modem} -M {max} -c '{commands}'".format(at_timeout=SENT_AT_TIMEOUT, path=API_PATH, file=AT_API_FILE, pw=HOST_PASSWORD, mmcli_timeout=MMCLI_TIMEOUT, modem=modem, max=MMCLI_MAX_TRY, commands=at_cmd )
        #print(linux_cmd)
        result = os.popen(linux_cmd).readlines()
        result = "".join(result)
        if(pats):
            result = checkRE(pats,result)
    return result

      
def getModem():
    result = None
    txt = os.popen('mmcli -L').readlines()
    pats=["/org/freedesktop/ModemManager1/Modem/\d","/Modem/\d","\d"]
    result = checkRE(pats,txt)
    return result


def getModule():
    result = None
    for module in MODULE:
        r = os.popen('lsusb|grep {}'.format(module)).readlines()
        if r:
            result = module
    return result
        


class Modem:
    def __init__(self, module_name="Fibocom", modem_num=0):
        self.update_info()

    def update_info(self):
        self.module_name = getModule()   
        self.modem_num = getModem()   
        self.ip     = self.get_ip_from_at()
        self.imsi   = self.get_imsi()
        self.sa     = self.get_sa()
        self.mobile = self.get_mobile()
        self.band   = self.get_band_from_at()
        self.apn    = self.get_apn_from_at()
        self.cops   = self.get_cops_from_at()
        self.auto_reg = self.get_auto_registration()

    # AT Commands 
    def send_at(self):
        cmd = "AT\r"
        return run(self.modem_num, cmd)

    def get_imsi(self):  
        if(self.module_name == FIBOCOM):
            cmd = 'AT+CIMI?'
            pats = [ "CIMI+: \d{15}", "\d{15}" ]
        elif(self.module_name == SIERRA):
            cmd=""
            pats=[]
        else:
            return ""
        return run(self.modem_num, cmd,pats)


    def set_auto_registration(self ):
        #logging.info('Set AUTO REG ')
        if(self.module_name == FIBOCOM):
            cmd = 'AT+GTAUTOCONNECT=1'
        elif(self.module_name == SIERRA):
            cmd=""
            pats=[]
        else:
            return ""
        return run(self.modem_num, cmd)


    def get_auto_registration(self):
        if(self.module_name == FIBOCOM):
            cmd = 'AT+GTAUTOCONNECT?'
            pats = ["GTAUTOCONNECT: \d","\d"]
        elif(self.module_name == SIERRA):
            cmd=""
            pats=[]
        else:
            return ""
        return run(self.modem_num, cmd,pats)


    def set_sa(self,ena):
        #logging.info('Set SA to '+str(ena))
        if(self.module_name == FIBOCOM):
            cmd ="AT+GTSET=\"5GSACTR\",{}".format(str(ena))
        elif(self.module_name == SIERRA):
            cmd=""
            pats=[]
        else:
            return ""
        return run(self.modem_num, cmd)
    

    def get_sa(self):
        if(self.module_name == FIBOCOM):
            cmd = "AT+GTSET?"
            pats = ["GTSET: \"5GSACTR\",\d" ,"\"5GSACTR\",\d",",\d","\d"]
        elif(self.module_name == SIERRA):
            cmd=""
            pats=[]
        else:
            return ""
        return run(self.modem_num, cmd,pats)


    def set_band_from_at(self, band):
        #logging.info('Set BAND to '+str(band))
        if(self.module_name == FIBOCOM):
            cmd = "AT+GTACT=14,,,{}\r\n".format(band)
        elif(self.module_name == SIERRA):
            cmd=""
            pats=[]
        else:
            return ""
        return run(self.modem_num, cmd)


    def get_band_from_at(self):
        if(self.module_name == FIBOCOM):
            cmd = "AT+GTACT?"
            pats = ["(,)+\d\d\d\d","50\d\d"]
        elif(self.module_name == SIERRA):
            cmd=""
            pats=[]
        else:
            return ""
        return run(self.modem_num, cmd,pats)


    def get_apn_from_at(self):
        if(self.module_name == FIBOCOM):
            cmd = "AT+CGDCONT?"
            pats = ["CGDCONT: 1,\"IP(V4V6)*\",\".*?\"," , "\",\".*?\"," ,',".*"','".*"']
        elif(self.module_name == SIERRA):
            cmd=""
            pats=[]
        else:
            return ""
        return run(self.modem_num, cmd,pats)


    def set_apn_from_at(self,apn):
        #logging.info('Set APN to '+str(apn))
        if(self.module_name == FIBOCOM):
            cmd = "AT+CGDCONT=1,\"IP\",\"{}\"".format(apn)
        elif(self.module_name == SIERRA):
            cmd=""
            pats=[]
        else:
            return ""
        return run(self.modem_num, cmd)


    def get_cops_from_at(self):
        if(self.module_name == FIBOCOM):
            cmd = "AT+COPS?"
            pats = ["COPS: .*\d*"]# end of 11 is "NR Connect to 5GCN"
        elif(self.module_name == SIERRA):
            cmd=""
            pats=[]
        else:
            return ""
        return run(self.modem_num, cmd,pats)


    def get_ip_from_at(self):
        reg_ip =  "((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])"
        if(self.module_name == FIBOCOM):
            cmd = "AT+CGDCONT?\r"
            pats = ["CGDCONT: 1,\"IP(V4V6)*\",\".*?\",\".*?\""  ,  reg_ip]
        elif(self.module_name == SIERRA):
            cmd=""
            pats=[]
        else:
            return ""
        return run(self.modem_num, cmd,pats)


    def get_call_info_from_at(self): ## TBD : modify to C
        #AT+GTCCINFO?\r\r\n+GTCCINFO:\r\nNR service cell:\r\n1,9,1,01,1,1,9E040,1,5078,100,89,60,60,65\r\n\r\n\r\nOK\r\n'
        if(self.module_name == FIBOCOM):
            cmd = "AT+GTCCINFO?"
            pats = [ "(\d{1,3},){1,6}\w{1,6},(\d*,){0,7}.*,\d*","(\d{1,3},){1,6}\w{1,6},(\d*,){0,7}.*,\d*"]
        #"\d\w{0,4}(,\w{1,5}){13}"
        elif(self.module_name == SIERRA):
            cmd=""
            pats=[]
        else:
            return ""
        return run(self.modem_num, cmd,pats)


    def set_mobile(self,ena):
        #logging.info('Set mobile to '+str(ena))
        if(self.module_name == FIBOCOM):
            cmd = "AT+CFUN={}".format(ena)
        elif(self.module_name == SIERRA):
            cmd=""
            pats=[]
        else:
            return ""
        return run(self.modem_num, cmd)


    def get_mobile(self):
        if(self.module_name == FIBOCOM):
            cmd = "AT+CFUN?"
            pats=["CFUN: \d,","\d"]
        elif(self.module_name == SIERRA):
            cmd=""
            pats=[]
        else:
            return ""
        return run(self.modem_num, cmd,pats)
    

    def get_signal(self):
        #logging.debug("Get Signal")
        result={
                "mcc" :"Not Found",
                "mnc" :"Not Found",
                "cellid" :"Not Found",
                "band" :"No Service",
                "bandwidth" :"No Service",
                "sinr" :"NA.",
                "rsrp" :"NA.",
                "rsrq" :"NA.",
        }
        debug_msg=""
        signals = self.get_call_info_from_at()
        logging.debug(signals) 
        if(signals):
            sig_info = signals.split(",")
            if( sig_info[0] == "1" ):
                debug_msg += "Is Service Call"
                if( sig_info[1] == "9" ):
                    debug_msg += "NR-RAN"
                    result["mcc"] = sig_info[2]
                    result["mnc"] = sig_info[3]
                    result["cellid"] = sig_info[5]
                    result["band"] = sig_info[8]
                    result["bandwidth"] = sig_info[9]
                    result["sinr"] = sig_info[11]
                    result["rsrp"] = sig_info[12]
                    result["rsrq"] = sig_info[13]
                else:
                    debug_msg += "No 5G Service"
                    debug_msg += "Return Error"
            else:
                debug_msg += "No Service Call"
                debug_msg += "Return Error"
        else:
            debug_msg ="Not get Result"
        logging.info(result)
        return result

    ##
    ## APIs by AT command
    ##

    def set_module_config(self, config):
    
        self.set_sa(config.get("SA"))
        self.set_band_from_at(config.get("BAND"))
        self.set_apn_from_at(config.get("APN"))
        self.set_auto_registration()
    
        return True


    def get_module_info(self):
        #logging.debug("Get Informations")
        info = {"IP":self.ip, "IMSI":self.imsi, "SA":self.sa, "BAND":self.band, "APN":self.apn, "COPS":self.cops ,"AUTOREG":self.auto_reg}
        logging.info(info)
        
        return info





##
## Main / Test
##
def main():
    #logging.info('== START ==')
    test_config = {"SA":1, "BAND":5079, "APN":"internet"}
    test_config2 = {"SA":1, "BAND":5078, "APN":"aaa.net"}
    modem = Modem()
    #modem.set_module_config(test_config2)
    #modem.update_info()
    #r1 = modem.get_module_config()
    #print(r1)

    modem.set_mobile(1)
    #modem.set_module_config(test_config)
    
    modem.update_info()
    r2 = modem.get_module_info()
    r3 = modem.get_signal()
    
    modem.set_mobile(0)
    
    #logging.info('== DONE ==')
    #logging.debug('debug')
    #logging.info('info')
    #logging.warning('warning')
    #logging.error('error')
    #logging.critical('critical')
if __name__ == '__main__' :
    print("=== START ===\n\n")
    main()
    
  
    print("\n\n=== DONE ===")
