import mido
import struct

# --- CONFIG ---
mid = mido.MidiFile('x.mid') # change the name here
START_BAR, END_BAR = 1, 150 # 80, 96
TICKS_PER_BAR = mid.ticks_per_beat * 4
start_tick = (START_BAR - 1) * TICKS_PER_BAR
end_tick = END_BAR * TICKS_PER_BAR

all_notes_in_range = []
active_notes = {}

for track in mid.tracks:
    current_tick = 0
    for msg in track:
        current_tick += msg.time
        if msg.type == 'note_on' and msg.velocity > 0:
            active_notes[msg.note] = current_tick
        elif (msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0)) and msg.note in active_notes:
            st = active_notes.pop(msg.note)
            if st >= start_tick and current_tick <= end_tick:
                all_notes_in_range.append({
                    'pitch': msg.note,
                    'start': float(st - start_tick),
                    'dur': float(current_tick - st)
                })

all_notes_in_range.sort(key=lambda x: x['start'])

def float_to_bin(f):
    return bin(struct.unpack('!I', struct.pack('!f', f))[0])[2:].zfill(32)

binary_output = ""
for n in all_notes_in_range:
    binary_output += format(n['pitch'], '08b')
    binary_output += float_to_bin(n['start'])
    binary_output += float_to_bin(n['dur'])

with open("full.txt", "w") as f:
    f.write(binary_output)

print(f"Sorted binary saved, encoded {len(all_notes_in_range)} notes.")