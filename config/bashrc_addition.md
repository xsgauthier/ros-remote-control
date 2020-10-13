# Robot auto-start
* Enable Auto-login in raspi-config
* sudo apt install screen
* Fill-up additional files (see below)
* reboot

The startup terminal will be available under screen ROBOT. screen -ls to list screens, screen -x to attach see screen utility help.

## Add this to .bashrc

```sh
echo "Source ROS"
source /opt/ros/melodic/setup.bash
echo "Source CAMERA"
source ~/camera_ws/install/setup.bash
echo "Source REMOTE"
source ~/remote_ws/install/setup.bash

export ROS_IP=`ip addr | grep 'inet 192\.168' | cut -d ' ' -f 6 | cut -d '/' -f 1`
export ROS_MASTER_URI=http://$ROS_IP:11311
echo "ROS_MASTER_URI=$ROS_MASTER_URI"

THIS_TTY=$(tty)

if [ $THIS_TTY == "/dev/tty1" ]
then
        screen -d -m -S ROBOT ~/launch_robot.sh
fi
```

## ~/launch_robot.sh

```sh
roslaunch camera_ws/config/camera.launch remote_ws/config/remote.launch
```
