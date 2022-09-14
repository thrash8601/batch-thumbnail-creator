import cv2
import os
import time
import math
from PIL import Image, ImageDraw, ImageFont


def get_video_length(video):
    frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
    frame_per_second = video.get(cv2.CAP_PROP_FPS)
    duration = frame_count / frame_per_second
    return frame_count, duration


if not os.path.exists('.tmp'):
    os.mkdir('.tmp')


required_screens = 9
video_file = 'test2.mp4'
cam = cv2.VideoCapture(video_file)
img_file = 'thumbs/' + video_file + '.jpg'
fc, dur = get_video_length(cam)
frame_distance = fc / required_screens

screen_size = (900, 900)

print('frame count: ' + str(fc))
print('duration: ' + str(dur))

images = []

for i in range(0, required_screens):
    frame_no = int(i * frame_distance)
    cam.set(1, frame_no)
    ret, frame = cam.read()
    name = './.tmp/frame' + str(i) + '.jpg'
    if ret:
        print('Creating...' + name)
        cv2.imwrite(name, frame)
        images.append(Image.open(name))
    else:
        print('Error capturing ' + name)

cam.release()
cv2.destroyAllWindows()

img = Image.new(mode="RGB", size=screen_size)

columns = math.floor(math.sqrt(required_screens))
rows = math.ceil(math.sqrt(required_screens))
print('cols: ' + str(columns))
print('rows: ' + str(rows))


def get_position(arr_index):
    if arr_index == 0:
        return 0, 0
    if arr_index == 1:
        return 1, 0
    if arr_index == 2:
        return 2, 0
    if arr_index == 3:
        return 0, 1
    if arr_index == 4:
        return 1, 1
    if arr_index == 5:
        return 2, 1
    if arr_index == 6:
        return 0, 2
    if arr_index == 7:
        return 1, 2
    if arr_index == 8:
        return 2, 2


for f in images:
    i = images.index(f)
    col, row = get_position(i)
    f.thumbnail((300, 300))
    img.paste(f, (col * 300, row * 300))

img.save(img_file, quality=95)
