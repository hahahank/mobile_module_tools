DATE=`date '+%Y-%m-%d %H:%M:%S'`

SLEEP=10



python3 /opt/fibocom_ubuntu/service/sendAT.py -e SET_N79



STATUS_CHANGE=true
while :
do
    python3 /opt/fibocom_ubuntu/service/modem.py

# End Loop
    sleep $SLEEP;
done



