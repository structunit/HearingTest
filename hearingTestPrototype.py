

"""Play a fixed frequency sound."""
from __future__ import division
import math
import pyaudio
import numpy

try:
    from itertools import izip
except ImportError: # Python 3
    izip = zip
    xrange = range


FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

p = pyaudio.PyAudio()


def data_for_freq(frequency: float, time: float = None):
    """get frames for a fixed frequency for a specified time or
    number of frames, if frame_count is specified, the specified
    time is ignored

    Source: https://stackoverflow.com/questions/974071/python-library-for-playing-fixed-frequency-sound
    """
    frame_count = int(RATE * time)

    remainder_frames = frame_count % RATE
    wavedata = []

    for i in range(frame_count):
        a = RATE / frequency  # number of frames per wave
        b = i / a
        # explanation for b
        # considering one wave, what part of the wave should this be
        # if we graph the sine wave in a
        # displacement vs i graph for the particle
        # where 0 is the beginning of the sine wave and
        # 1 the end of the sine wave
        # which part is "i" is denoted by b
        # for clarity you might use
        # though this is redundant since math.sin is a looping function
        # b = b - int(b)

        c = b * (2 * math.pi)
        # explanation for c
        # now we map b to between 0 and 2*math.PI
        # since 0 - 2*PI, 2*PI - 4*PI, ...
        # are the repeating domains of the sin wave (so the decimal values will
        # also be mapped accordingly,
        # and the integral values will be multiplied
        # by 2*PI and since sin(n*2*PI) is zero where n is an integer)
        d = math.sin(c) * 32767
        e = int(d)
        wavedata.append(e)

    for i in range(remainder_frames):
        wavedata.append(0)

    stereo_signal = numpy.zeros([len(wavedata), 2])  # these two lines are new
    stereo_signal[:, 0] = wavedata[:]  # 1 for right speaker, 0 for  left

    wavedata = stereo_signal.astype(numpy.int16).tostring()
    return wavedata


def play(frequency: float, time: float):
    """
    play a frequency for a fixed time!
    """
    frames = data_for_freq(frequency, time)
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True)
    stream.write(frames)
    stream.stop_stream()
    stream.close()


if __name__ == '__main__':
    print("Welcome to the Test you hearing prototype!")

    freq = list(range(10, 100, 10)) + list(range(100, 1000, 50)) + list(range(1000, 9000, 200))
    freq_list = list(range(4000, 9000, 200))
    for f in freq_list:
        print(f, "Hz")
        play(f, 0.2)

