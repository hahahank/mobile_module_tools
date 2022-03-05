echo "Update usbnet driver" 
sudo modprobe -r qmi_wwan
sudo modprobe -r GobiNet
sudo modprobe usbnet
sudo modprobe GobiNet
sleep 3
lsmod|grep usbnet

while [ ! -d /sys/class/net/usb0 ]
do
    echo "Interface not found ... "
    sudo modprobe -r qmi_wwan
    sudo modprobe -r GobiNet
    sudo modprobe usbnet
    sudo modprobe GobiNet
    sleep 3
done
echo "Update driver DONE"
lsmod|grep usbnet
