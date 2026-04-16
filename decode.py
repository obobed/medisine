import numpy as np
from scipy.io import wavfile
import struct

def bin_to_float(b):
    return struct.unpack('!f', struct.pack('!I', int(b, 2)))[0]

with open("result/full.txt", "r") as f:
    binary_data = f.read()

# SET BPM HERE
TARGET_BPM = 186
SAMPLE_RATE = 44100
TICKS_PER_BEAT = 480 
seconds_per_tick = (60 / TARGET_BPM) / TICKS_PER_BEAT

notes = []
chunk_size = 72 

for i in range(0, len(binary_data), chunk_size):
    chunk = binary_data[i:i+chunk_size]
    if len(chunk) < chunk_size: break
    notes.append({
        'freq': 440 * (2**((int(chunk[0:8], 2) - 69) / 12)),
        'start': bin_to_float(chunk[8:40]) * seconds_per_tick,
        'duration': bin_to_float(chunk[40:72]) * seconds_per_tick
    })

# Render
max_time = max(n['start'] + n['duration'] for n in notes)
audio_buffer = np.zeros(int(SAMPLE_RATE * (max_time + 1)))

for n in notes:
    t = np.linspace(0, n['duration'], int(SAMPLE_RATE * n['duration']), endpoint=False)
    envelope = np.exp(-3 * t / n['duration'])
    wave = 0.5 * np.sin(2 * np.pi * n['freq'] * t) * envelope
    start_sample = int(n['start'] * SAMPLE_RATE)
    audio_buffer[start_sample : start_sample + len(wave)] += wave

audio_buffer /= np.max(np.abs(audio_buffer))
wavfile.write('result/full.wav', SAMPLE_RATE, (audio_buffer * 32767).astype(np.int16))