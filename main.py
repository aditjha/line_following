#!/usr/bin/env python
from __future__ import print_function
import rospy
import sys
import cv2
import os
import yaml
import time

from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from ackermann_msgs.msg import AckermannDriveStamped

from pid import PID
from controller import Controller
from imageconverter import ImageConverter

def image_callback(data, args):
    params = args[0]
    control_class = args[1]
    bridge = args[2]
    image_converter_class = args[3]
    cv_image = bridge.imgmsg_to_cv2(data, "bgr8")
    err, img = image_converter_class.get_centerline_pixel(cv_image, params["target_height_line"], params["threshold"], params["rows_checked"])
    control_class.err = err
    control_class.img = img
    #print('end')

def publish_control(control, publisher, params):
    ctrlmsg = AckermannDriveStamped()
    ctrlmsg.header.stamp = rospy.Time.now()
    ctrlmsg.drive.speed = params['speed']
    ctrlmsg.drive.steering_angle = control
    publisher.publish(ctrlmsg)

def load_params():
    '''
    Loads params from /config/config.yaml
    '''
    src_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    rel_path = '/config/'
    filename = 'config.yaml'
    with open(src_dir+rel_path+filename, 'r') as stream:
        config = yaml.safe_load(stream)
    return config


def main(args, params):
    rospy.init_node('aaas-demo', anonymous=True)
    print("RUNNING AAAS Demo")

    # Init components
    ic = ImageConverter(params)
    pid = PID(params)
    controller = Controller(params) # not a controller
    bridge = CvBridge()
    
    # Init Publishers/Subscribers
    image_pub = rospy.Publisher("/edge_detection_image", Image, queue_size=2)
    image_sub = rospy.Subscriber("/camera/color/image_raw", Image, image_callback, (params, controller, bridge, ic))
    control_pub = rospy.Publisher("mux/ackermann_cmd_mux/input/navigation", AckermannDriveStamped, queue_size=1)

    directional_err = 0
    rate = rospy.Rate(params['pub_rate'])
    while not rospy.is_shutdown():

        if controller.err is not None: # Only run if there is a line reading
            steering_angle = pid.get_control(controller.err, ic.image_width)
            publish_control(steering_angle, control_pub, params)
            if controller.err != 0:
                directional_err = -1 *(controller.err / abs(controller.err))
            else:
                directional_err = 0
        else:
            if directional_err == 0:
                publish_control(0, control_pub, params)
            else:
                print('lost line')
                publish_control(directional_err*0.34, control_pub, params)

        if params["publish_images_rviz"]:
            image_pub.publish(bridge.cv2_to_imgmsg(controller.img, "mono8"))

        rate.sleep()

if __name__ == '__main__':
    params = load_params()
    main(sys.argv, params)
