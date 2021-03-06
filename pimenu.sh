#!/bin/bash
#
# Any action tile (eg. any tile with no sub items) will trigger this script.
# The names of the pages and of the clicked tile will be passed as arguments.
# Use those to decide what to do.

key=${@: -1}

PIMENUDIR="/home/pi/Scripts/pimenu/"
SCRIPTSDIR="/home/pi/Scripts/"

USBKEYS=($(
    grep -Hv ^0$ /sys/block/*/removable |
    sed s/removable:.*$/device\\/uevent/ |
    xargs grep -H ^DRIVER=sd |
    sed s/device.uevent.*$/size/ |
    xargs grep -Hv ^0$ |
    cut -d / -f 4
))

USBMOUNT=($(mount | grep /dev/$USBKEYS | awk '{print $3}' | grep RASPI-DATA))
# The first detected USB key
#USBMOUNT=($(mount | grep /dev/$USBKEYS | awk '{print $3}'))

case $key in
    "freemem")
    	sync
		sudo echo 3 > /proc/sys/vm/drop_caches
    ;;
    "start")
    	killall pimenu.py
    	$PIMENUDIR/pimenu.py fs
    ;;
    "photoframe")
		$SCRIPTSDIR/picture_frame.sh $USBMOUNT
    ;;
    "reboot")
    	sudo reboot
    ;;
    "shutdown")
    	sudo shutdown -h now
    ;;
    "usb")
        cd
        if [ ! -d "PHOTOS" ]; then
            mkdir PHOTOS
        fi
        USB_MOUNT_POINT=$(find /media/ -mindepth 1 -maxdepth 1 -not -empty -type d | \
                          sed 's/ /\\ /g')
        exiftool -r -d /home/pi/PHOTOS/%Y%m%d-%H%M%S.%%e '-FileName<DateTimeOriginal' \
                $USB_MOUNT_POINT >> /home/pi/transfer.log
    ;;
    "backup")
    	$SCRIPTSDIR/backup.sh &
    ;;
    "displayoff")
    	$SCRIPTSDIR/screen.sh off
    ;;
    "displayon")
    	$SCRIPTSDIR/screen.sh on
    ;;
    "")
        ps aux | grep -ie pimenu | awk '{print $2}' | xargs kill -9
    ;;
esac

#sleep 3
