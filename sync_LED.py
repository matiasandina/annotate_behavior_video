# import the necessary packages
from collections import deque
import numpy as np
import cv2
import time
import imutils
import itertools
from deques_to_table import deques_to_table
from crop_deque import crop_deque

def sync_LED(videofile, output_filename, trial_length = 10000):

    vs = cv2.VideoCapture(videofile)

    # allow the camera or video file to warm up
    time.sleep(1.0)

    # keep iter number
    iter_num = 0

    # make a deque for keeping values
    dot_detected = deque(maxlen=100)
    time_deque = deque(maxlen=100)
    iter_deque = deque(maxlen=100)

    while True:

        # grab the current frame
        frame = vs.read()


       # if we are viewing a video and we did not grab a frame,
       # then we have reached the end of the video
        if frame is None:
            break

        frame = frame[1]


        # resize the frame, blur it, and convert it to the HSV
        # color space
        # frame = cv2.resize(frame, (600,800))
        blurred = cv2.GaussianBlur(frame, (5, 5), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        # construct a mask for the marbles and mice, then perform

        HSV_min = (47, 153, 136)
        HSV_max = (181, 255, 255)

        binarymask = cv2.inRange(hsv, HSV_min, HSV_max)

        if iter_num == 0:
            showCrosshair = False
            fromCenter = False
            region = cv2.selectROI("Image", frame, fromCenter, showCrosshair)

    # Crop image always on region

        imCrop = binarymask[int(region[1]):int(region[1] + region[3]), \
             int(region[0]):int(region[0] + region[2])]

        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        cnts = cv2.findContours(imCrop.copy(),
                                cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
    

        # Get the contours considering different openCV versions
        cnts = imutils.grab_contours(cnts)


        # only do math if you have detections
        # because area is small and we have good SNR, checking the length might be enough...
        # TODO: This might not always be the case
    
        if len(cnts) > 0:
            dot_detected.append(1)
        else:
            dot_detected.append(0)
    
        # append time and iter_num deques
        time_deque.append(time.time())
        iter_deque.append(iter_num)

        

        # Convert to array to save
        # Wait until the iteration number is divisible by the buffer length
        if (iter_num % 100 == 0):

            # Prepare with helper and SAVE
            array_to_save = deques_to_table(dot_detected, time_deque)

            array_to_save = deques_to_table(array_to_save, iter_deque)

            # Save to file
            with open(output_filename, 'a') as outfile:
                np.savetxt(outfile, array_to_save,
                           delimiter=',', fmt='%s')
    
            # Adjust and print info
            last_saved = iter_num
            print("Saving on iteration..." + str(last_saved))
    
        # Add if statement to avoid showing videos for efficiency
        # show the videos to our screen
        cv2.imshow("Frame", frame)
        cv2.imshow("Binarymask", binarymask)
        cv2.imshow("Region", imCrop)
    
        #### Kill the process ######
        key = cv2.waitKey(1) & 0xFF
    
        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            break
    
        iter_num = iter_num + 1
    
        if iter_num > trial_length:
            print("Breaking at iteration " + str(trial_length))

            # Save last info

            # On exit, keep the last frames in buffer
            # These weren't saved because iteration_number was not multiple of buffer

            # Subset the deques
            # The reminder of this division will give the unsaved elements
            unsaved_elements = iter_num % last_saved

            # Crop with helper
            dot_detected = crop_deque(dot_detected, unsaved_elements)
            time_deque = crop_deque(time_deque, unsaved_elements)
            iter_deque = crop_deque(iter_deque, unsaved_elements)

            # Prepare with helper and SAVE
            array_to_save = deques_to_table(dot_detected, time_deque)

            array_to_save = deques_to_table(array_to_save, iter_deque)

            # Save to file
            with open(output_filename, 'a') as outfile:
                np.savetxt(outfile, array_to_save,
                           delimiter=',', fmt='%s')




            break
    
    cv2.destroyAllWindows()
    return "Done :)"