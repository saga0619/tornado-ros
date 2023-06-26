import rospy
from std_msgs.msg import String

import json
import datetime


def talker():
    pub = rospy.Publisher('chatter', String, queue_size=10)
    rospy.init_node('talker', anonymous=True)

    rate = rospy.Rate(100) # 10hz
    while not rospy.is_shutdown():

        # make the time string with current time, and publish it. 
        # now = year-month-day hour:minute:second.millisecond
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")





        pub.publish(str(now))
        rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass