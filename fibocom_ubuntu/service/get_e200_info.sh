DATE=`date '+%Y-%m-%d %H:%M:%S'`

SLEEP=120







STATUS_CHANGE=true
while :
do
    python3 /opt/fibocom_ubuntu/service/modem.py

# End Loop
    sleep $SLEEP;
done



