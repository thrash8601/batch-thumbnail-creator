import cv2
import os
import math
from PIL import Image, ImageDraw, ImageFont
import argparse
from pymediainfo import MediaInfo

required_screens = 9
video_dir = 'Videos/'
screen_size = (900, 900)

parser = argparse.ArgumentParser()
# Right now -d needs to be the "Videos" dir in the current dir, as hardlinks seem to break opencv
parser.add_argument('-d', help='Directory of files to create thumbs of', type=str, nargs='?', const=True, default='')
parser.add_argument('-f', help='Single file to screencap', type=str, nargs='?', const=True, default='')
args = parser.parse_args()
folder = args.d
file = args.f

if not file and not folder:
    raise Exception('You need to define a file or dir')


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


def get_file_size(file_dir):
    file_stats = os.stat(file_dir)
    b_count = file_stats.st_size
    if b_count > (1024 * 1024 * 1024 * 1024):
        return str(round(b_count / (1024 * 1024 * 1024 * 1024), 2)) + 'tb'
    if b_count > (1024 * 1024 * 1024):
        return str(round(b_count / (1024 * 1024 * 1024), 2)) + 'gb'
    if b_count > (1024 * 1024):
        return str(round(b_count / (1024 * 1024), 2)) + 'mb'
    if b_count > 1024:
        return str(round(b_count / 1024, 2)) + 'kb'


def get_number_as_2_places(num):
    if num < 10:
        return '0' + str(num)
    return str(num)


def get_duration(full_duration):
    secs = full_duration / 1000
    hours = secs / 3600
    minutes = (hours % 1) * 60
    secs = (minutes % 1) * 60

    hours = get_number_as_2_places(math.floor(hours))
    minutes = get_number_as_2_places(math.floor(minutes))
    secs = get_number_as_2_places(math.floor(secs))

    duration = f'{hours}:{minutes}:{secs}'
    return duration


def get_media_info(file_dir):
    media_info = MediaInfo.parse(file_dir)
    vid_track = media_info.video_tracks[0]
    ret = {}
    ret['filename'] = file_dir.split('/')[-1]
    ret['size'] = get_file_size(file_dir)
    ret['bitrate'] = vid_track.other_bit_rate[0]
    ret['duration'] = get_duration(vid_track.duration)
    ret['framerate'] = vid_track.frame_rate
    ret['resolution'] = str(vid_track.width) + ' / ' + str(vid_track.height)
    return ret


def generate_file_info(vid):
    img = Image.new("RGB", (1100, 150), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    font_size = 16
    font = ImageFont.truetype("Roboto-Regular.ttf", font_size)
    header = ImageFont.truetype("Roboto-Bold.ttf", 20)
    gap = 5
    info = get_media_info(vid)
    draw.text((0, 0), f"{info['filename']}", (0, 0, 0), font=header)
    draw.text((0, 20 + gap + font_size), f"Size: {info['size']}", (0, 0, 0), font=font)
    draw.text((0, 20 + gap * 2 + font_size * 2), f"Bitrate: {info['bitrate']}", (0, 0, 0), font=font)
    draw.text((0, 20 + gap * 3 + font_size * 3), f"Framerate: {info['framerate']}", (0, 0, 0), font=font)
    draw.text((0, 20 + gap * 4 + font_size * 4), f"Resolution: {info['resolution']}", (0, 0, 0), font=font)
    draw.text((0, 20 + gap * 5 + font_size * 5), f"Duration: {info['duration']}", (0, 0, 0), font=font)
    return img


def generate_screen(images, filename, video_file_name):
    img = Image.new(mode="RGB", size=(1000, 1200), color=(255, 255, 255))
    info = generate_file_info(video_file_name)
    img.paste(info, (50, 50))
    screens = Image.new(mode="RGB", size=screen_size, color=(255, 255, 255))
    for f in images:
        i = images.index(f)
        col, row = get_position(i)
        f.thumbnail((300, 300))
        screens.paste(f, (col * 300, row * 300))
    img.paste(screens, (50, 250))
    img.save(filename, quality=95)


def run(d=None, f=None):
    if d:
        video_files = get_video_files(d)
    elif f:
        video_files = [f]

    for vid in video_files:
        cam = cv2.VideoCapture(vid)
        filename = vid.split('/')[-1]
        print('Processing ' + filename + '...')
        img_file = 'thumbs/' + filename + '.jpg'
        fc, dur = get_video_length(cam)
        frame_distance = fc / required_screens
        images = generate_thumbs(cam, frame_distance)
        generate_screen(images, img_file, vid)
        cam.release()


run(folder, file)
