import os
import subprocess

ABSOLUTE_LOCATION = os.path.dirname(os.path.realpath(__file__))
# TEST_LANG_DATA = os.path.join(os.getcwd(), "test_semantics.csv")

TEST_LANG_DATA = os.path.join(ABSOLUTE_LOCATION, "data_to_burn.csv")

BACKGROUNDS_DIR = os.path.join("/home/gloryi/Pictures/FlickrSets/geo_images")

#NEXT_APP_DIR = "/mnt/X/WORKSHOP/Scripts/stocks_learning_git/experimental_learning_tools"
NEXT_APP_DIR = "/mnt/X/WORKSHOP/Scripts/chained_learning"
NEXT_APP = os.path.join(NEXT_APP_DIR, "app.py")

HAPTIC_PATH = "/home/gloryi/Documents/SpecialFiles/xbox_haptic/haptic_ultimate"
DEVICE_NAME = "/dev/input/by-id/usb-Microsoft_Controller_7EED82417161-event-joystick"

def HAPTIC_FEEDBACK(lower_freq=500, higher_freq=50000, duration=995):
    command = " ".join([HAPTIC_PATH, DEVICE_NAME,
                        str(lower_freq), str(higher_freq), str(duration)])
    subprocess.Popen(command, shell=True)

DATA_SIZE = 50
MINOR_IMAGES_H = 80 
