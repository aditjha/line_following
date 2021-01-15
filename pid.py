import numpy as np
import time
from math import pi

class PID:
    def __init__(self, params):
        # initialze gains
        self.params = params
        self.Kp = self.params['Kp']
        self.Kd = self.params['Kd'] 
        self.Ki = self.params['Ki'] 

        # initialize delta t variables
        self.currtm = time.time()
        self.prevtm = self.currtm

        self.prev_err = 0

        # term result variables
        self.Cp = 0
        self.Ci = 0
        self.Cd = 0

    def image_pixel_mapping(self, input, image_width):
        return input * 100 / (image_width / 2)
    
    def degrees_to_radians(self, input):
        return input * pi / 180

    def get_control(self, center_offset, image_width):
        center_offset_scaled = self.image_pixel_mapping(center_offset, image_width)
        self.currtm = time.time()               # get t
        dt = self.currtm - self.prevtm          # get delta t
        de = center_offset_scaled - self.prev_err              # get delta error

        self.Cp = self.Kp * center_offset_scaled              # proportional term
        
        self.Ci += center_offset_scaled * dt                   # integral term

        self.Cd = 0
        if dt > 0:                              # no div by zero
            self.Cd = de/dt                     # derivative term

        self.prevtm = self.currtm               # save t for next pass
        self.prev_err = center_offset_scaled                   # save t-1 error

            # sum the terms and return the result
        u = - (self.Cp + (self.Ki * self.Ci) + (self.Kd * self.Cd))
        #print("PID In_Out_P_I_D: " + str(center_offset_scaled) + "_" + str(u) + "_" + str(self.Cp) + "_" + str(self.Ki * self.Ci) + "_" + str(self.Kd * self.Cd))
        return self.degrees_to_radians(u)
