import os

ABSOLUTE_LOCATION = os.path.dirname(os.path.realpath(__file__))
# TEST_LANG_DATA = os.path.join(os.getcwd(), "test_semantics.csv")

TEST_LANG_DATA = os.path.join(ABSOLUTE_LOCATION, "data_to_burn.csv")

BACKGROUNDS_DIR = os.path.join("/home/gloryi/Pictures/FlickrSets/geo_images")

#NEXT_APP_DIR = "/mnt/X/WORKSHOP/Scripts/stocks_learning_git/experimental_learning_tools"
NEXT_APP_DIR = "/mnt/X/WORKSHOP/Scripts/chained_learning"
NEXT_APP = os.path.join(NEXT_APP_DIR, "app.py")

DATA_SIZE = 50
MINOR_IMAGES_H = 80 
