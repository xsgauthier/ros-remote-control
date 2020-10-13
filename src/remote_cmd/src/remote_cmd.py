#!/usr/bin/env python
from smbus2 import SMBus
import roslib; roslib.load_manifest('remote_cmd')
import rospy
import tf.transformations
from geometry_msgs.msg import Twist

bus = SMBus(1)

def callback(msg):
    #rospy.loginfo("Linear Components: [%f, %f, %f]"%(msg.linear.x, msg.linear.y, msg.linear.z))
    #rospy.loginfo("Angular Components: [%f, %f, %f]"%(msg.angular.x, msg.angular.y, msg.angular.z))

    #now = rospy.get_rostime()

    speed = int(150*msg.linear.x)
    twist = int(45*msg.angular.z)

    if twist < 0:
        bus.write_i2c_block_data(0x20, 0, [ int(256+twist), 0 ])
    else:
        bus.write_i2c_block_data(0x20, 0, [ int(twist), 0 ])

    if speed < 0:
	bus.write_i2c_block_data(0x04, 2, [ 0, int(-speed) ])
    elif speed > 0:
        bus.write_i2c_block_data(0x04, 1, [ 0, int(speed) ])
    else:
        bus.write_i2c_block_data(0x04, 0, [ 0, 0 ])

def listener():
    rospy.Subscriber("/cmd_vel", Twist, callback)

class SendEmptyWatchdog(object):
    def __init__(self, datatype, topic, timeout=0.15, send_value=None):
        self.timeout = timeout
        self.datatype = datatype

        if send_value is None:
            self.send_value = datatype()
        else:
            self.send_value = send_value

        self.twist_subscriber = rospy.Subscriber(topic, self.datatype, self.message_callback, queue_size=1)
        self.twist_publisher = rospy.Publisher(topic, self.datatype, queue_size=1)
        self.timer = rospy.Timer(rospy.Duration(self.timeout), self.timer_callback, oneshot=True)
        self.timeout_triggered = False

    def message_callback(self, msg):
        rospy.logdebug("SendEmptyWatchdog{}: Message Callback".format(self.datatype))
        if self.timeout_triggered:
            self.timeout_triggered = False
        else:
            self.timer.shutdown()
            self.timer = rospy.Timer(rospy.Duration(self.timeout), self.timer_callback, oneshot=True)

    def timer_callback(self, event):
        rospy.logwarn("SendEmptyWatchdog{}: Timeout Triggered. Received no message for {} seconds".format(self.datatype, self.timeout))

        self.timeout_triggered = True
        self.twist_publisher.publish(self.send_value)

if __name__ == '__main__':
    try:
        rospy.init_node('cmd_vel_listener')
        twist_watchdog = SendEmptyWatchdog(Twist, "cmd_vel", timeout=3.0)
    	listener()
        rospy.spin()
    finally:
        bus.close()
