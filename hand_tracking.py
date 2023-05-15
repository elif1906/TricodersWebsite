import cv2
import mediapipe as mp
from settings import *
mp_drawing_styles = mp.solutions.drawing_styles
mp_drawing = mp.solutions.drawing_utils # Initialize Mediapipe hands module
mp_hands = mp.solutions.hands

class HandTracking:
    def __init__(self):
        self.hand_tracking = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5,max_num_hands=1)
        #Maximum number of hands to detect.we can increase the detection hand, but for a faster and more accurate result, it is useful to specify as many hands as we will define.
        #mix_detection_confidence:the model will only consider hand detections that have a confidence score of at least 0.7 to be valid. Hand detections with a lower confidence score will be discarded.increasing the value can increase accuracy but decrease the number of hand detections likewise decreasing the value may give false results with too many detections
        #min_tracking_confidence:#this is the same think just track
        self.hand_x = 0  #initially define the position of the hand
        self.hand_y = 0
        self.results = None
        self.hand_closed = False



    def scan_hands(self, image):

        rows, cols, _ = image.shape

        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)  # 0 means flips the image vertically along the x-axis. 1 means image horizontally along the y-axis.
                                                 #the BGR image to RGB. because MediaPipe only works with RGB
        
        image.flags.writeable = False
        
        self.results = self.hand_tracking.process(image) #contains information about the location and state of any hands detected in the image.
        
        # Draw the hand annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        self.hand_closed = False  #means open hand # hand is open when a Hand object is created.

        if self.results.multi_hand_landmarks: #checks if there are any hand landmarks detected in the current frame.
            for hand_landmarks in self.results.multi_hand_landmarks: #if one or more hands detected, the code enters a for loop
                x, y = hand_landmarks.landmark[9].x, hand_landmarks.landmark[9].y
                self.hand_x = int(x * SCREEN_WIDTH)
                self.hand_y = int(y * SCREEN_HEIGHT)

                x1, y1 = hand_landmarks.landmark[12].x, hand_landmarks.landmark[12].y
                if y1 > y:
                    self.hand_closed = True
                    print("Hand closed")
                else:
                    print("Hand open")

                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())

        return image

    def get_hand_center(self):
        return (self.hand_x, self.hand_y)


    def display_hand(self):
        cv2.imshow("image", self.image)
        cv2.waitKey(1)

    def is_hand_closed(self):

        pass

