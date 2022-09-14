import cv2
import os
import time
import math
from PIL import Image, ImageDraw, ImageFont

required_screens = 9
video_dir = 'Videos/'
screen_size = (900, 900)


def get_video_length(video):
    frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
    frame_per_second = video.get(cv2.CAP_PROP_FPS)
    duration = frame_count / frame_per_second
    return frame_count, duration


if not os.path.exists('.tmp'):
    os.mkdir('.tmp')


def get_video_files(files_dir):
    files = os.listdir(files_dir)
    ret = []
    for file in files:
        f, ext = os.path.splitext(file)
        if ext == '.mp4':
            ret.append(files_dir + file)
    return ret


def generate_thumbs(video, frame_distance):
    thumbs_arr = []
    for i in range(0, required_screens):
        frame_no = int(i * frame_distance)
        video.set(1, frame_no)
        ret, frame = video.read()
        name = './.tmp/frame' + str(i) + '.jpg'
        if ret:
            cv2.imwrite(name, frame)
            thumbs_arr.append(Image.open(name))
        else:
            print('Error capturing ' + name)
    return thumbs_arr


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


def generate_screen(images, filename):
    img = Image.new(mode="RGB", size=screen_size)
    for f in images:
        i = images.index(f)
        col, row = get_position(i)
        f.thumbnail((300, 300))
        img.paste(f, (col * 300, row * 300))
    img.save(filename, quality=95)


def run():
    columns = math.floor(math.sqrt(required_screens))
    rows = math.ceil(math.sqrt(required_screens))

    video_files = get_video_files(video_dir)

    for vid in video_files:
        print('Processing ' + vid + '...')
        cam = cv2.VideoCapture(vid)
        filename = vid.split('/')[-1]
        img_file = 'thumbs/' + filename + '.jpg'
        fc, dur = get_video_length(cam)
        frame_distance = fc / required_screens
        images = generate_thumbs(cam, frame_distance)
        generate_screen(images, img_file)
        cam.release()


run()
