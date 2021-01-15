#!/usr/bin/env python
import cv2, time
import numpy as np


class ImageConverter:
    def __init__(self, params):
        self.params = params
        self.image_width = None


    # Returns a tuple of (err, image) where:
    #   err is line's pixel offset from center of image
    #   image is the edges detected with a line showing target height
    def get_centerline_pixel(self, img, target_height_from_bottom, threshold=50, rows_checked=10):
        self.image_width = img.shape[1]

        target_height = img.shape[0] - target_height_from_bottom
        assert target_height >= 0 and target_height < img.shape[0]

        start_row = target_height - rows_checked / 2
        
        img = img[start_row : (start_row + rows_checked), :, :]

        # Subtracts green channel by other two (to reduce value of white areas and focus on only green)
        img[:, :, 1] = cv2.subtract(img[:, :, 1], (img[:, :, 0] / 2) + (img[:, :, 2] / 2))
        # np.clip(img[: ,: ,1], 0, 255)
        # Zero out other two channels
        img[:, :, 0] = img[:, :, 1]
        img[:, :, 2] = img[:, :, 1]
        # Threshold and thn copy green channel to other channels
        ret, thresh = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
        thresh[:, :, 0] = thresh[:, :, 1]
        thresh[:, :, 2] = thresh[:, :, 1]
        # TODO: Handle return value
        # Convert to grayscale for edge detection
        green_gray = cv2.cvtColor(thresh, cv2.COLOR_BGR2GRAY)
        # Edge detection
        edges = cv2.Canny(green_gray, 50, 150, apertureSize=3)
        # Check the rows_checked amount of rows above and below target height
        
        average_result = 0
        valid_rows = 0
        for row in range(0, rows_checked):
            sum = 0
            count = 0
            i = 0
            # Check entire row for detected edges
            for pixel in edges[row, :]:
                if pixel > 0:
                    sum += i
                    count += 1
                if count > 2:
                    break
                i += 1
            # If there were two detected edges, it is considered a valid row.
            # TODO: Make less sensitive and able to handle more eror
            if count is 2:
                valid_rows += 1
                average_result += sum / 2
                return ((average_result / valid_rows) - (img.shape[1] / 2), edges)
                # edges[row, (sum / 2)] = 255 # Draw center on the image
        edges[rows_checked / 2, :] = 255

        if valid_rows == 0:
            # print "Unable to find any line, try adjusting threshold value"
            return (None, edges)
        (average_result / valid_rows) - (img.shape[1] / 2)
        return ((average_result / valid_rows) - (img.shape[1] / 2), edges)
