import argparse
import os
import random
import uuid

from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.io.ffmpeg_reader import FFMPEG_VideoReader


class FFMPEG_VideoReaderCustom(FFMPEG_VideoReader):
    """
        Этот метод вызывал баг, при котором скрипт не работал корректно,
        пришлось его немного изменить,
        удалив блок условия
    """

    def close(self):
        if self.proc:
            self.proc.terminate()
            self.proc.stdout.close()
            self.proc.stderr.close()
            self.proc.wait()
            self.proc = None


class VideoFileCustom(VideoFileClip):
    def __init__(self, filename, has_mask=False,
                 audio=True, audio_buffersize=200000,
                 target_resolution=None, resize_algorithm='bicubic',
                 audio_fps=44100, audio_nbytes=2, verbose=False,
                 fps_source='tbr'):
        super().__init__(filename, has_mask=False,
                         audio=True, audio_buffersize=200000,
                         target_resolution=None, resize_algorithm='bicubic',
                         audio_fps=44100, audio_nbytes=2, verbose=False,
                         fps_source='tbr')

        pix_fmt = "rgba" if has_mask else "rgb24"
        self.reader = FFMPEG_VideoReaderCustom(filename, pix_fmt=pix_fmt,
                                               target_resolution=target_resolution,
                                               resize_algo=resize_algorithm,
                                               fps_source=fps_source)


def video_clip_cut(file, seconds_start=0, seconds_end=2):

    """выбирает случайное видео из указанного файла и обрезает по указанным секундам"""

    video = random.choice(os.listdir(f'{file}/'))
    return VideoFileCustom(os.path.join(file, video)).subclip(seconds_start, seconds_end)


def audio_clip_cut(file, seconds_start=0, seconds_end=4):

    """выбирает случайное аудио из указанного файла и обрезает по указанным секундам"""

    audio = random.choice(os.listdir(f'{file}/'))
    return AudioFileClip(os.path.join(file, audio)).subclip(seconds_start, seconds_end)

# можно было бы объединить audio_clip_cut и video_clip_cut в одну функцию, но я предпочел разделить в угоду читаемости


parser = argparse.ArgumentParser(description=
                                 """
    Selects a random video from files file1 and file2
    then takes a random one from the music file,
    cuts the first and second videos to two seconds,
    merges them and overlays the music
                                             """)

# добавление Optional arguments
parser.add_argument('-f1', '--file1', type=str, help='first video file path')
parser.add_argument('-f2', '--file2', type=str, help='second video file path')
parser.add_argument('-m', '--music', type=str, help='music file path')
parser.add_argument('-o', '--fileout', type=str, help='output filename (without *.mp4)')

# Пространство имен с нашими переменными
args = parser.parse_args()

# соединение двух видео и музыки
final_clip = concatenate_videoclips([video_clip_cut(args.file1),
                                     video_clip_cut(args.file2)],
                                    method="compose").set_audio(audio_clip_cut(args.music))

# можно передать переменной -o название конечного файла,
# если переменная не будет передана, сгенерится случайное
final_clip.write_videofile(args.fileout + '.mp4' if args.fileout else str(uuid.uuid4()) + '.mp4')
