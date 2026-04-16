import mido
import struct

# --- CONFIG ---
mid = mido.MidiFile('x.mid') # change the name here
START_BAR, END_BAR = 1, 150 # 80, 96


def parse_midi_by_bars(mid_file, start_bar, end_bar):
    ticks_per_bar = mid_file.ticks_per_beat * 4
    start_tick = (start_bar - 1) * ticks_per_bar
    end_tick = end_bar * ticks_per_bar

    notes = []

    for track in mid_file.tracks:
        current_tick = 0
        active_notes = {}
        for msg in track:
            current_tick += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                active_notes[msg.note] = current_tick
            elif (msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0)) and msg.note in active_notes:
                st = active_notes.pop(msg.note)
                if st >= start_tick and current_tick <= end_tick:
                    notes.append({
                        'pitch': msg.note,
                        'start': float(st - start_tick),
                        'dur': float(current_tick - st)
                    })

    notes.sort(key=lambda x: x['start'])
    return notes


def parse_whole_midi(mid_file):
    notes = []

    for track in mid_file.tracks:
        current_tick = 0
        active_notes = {}
        for msg in track:
            current_tick += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                active_notes[msg.note] = current_tick
            elif (msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0)) and msg.note in active_notes:
                st = active_notes.pop(msg.note)
                notes.append({
                    'pitch': msg.note,
                    'start': float(st),
                    'dur': float(current_tick - st)
                })

    notes.sort(key=lambda x: x['start'])
    return notes

def float_to_bin(f):
    return bin(struct.unpack('!I', struct.pack('!f', f))[0])[2:].zfill(32)

binary_output = ""
#parsed_notes = parse_midi_by_bars(mid, START_BAR, END_BAR)
parsed_notes = parse_whole_midi(mid)
for n in parsed_notes:
    binary_output += format(n['pitch'], '08b')
    binary_output += float_to_bin(n['start'])
    binary_output += float_to_bin(n['dur'])

with open("result/full.txt", "w") as f:
    f.write(binary_output)

print(f"Sorted binary saved, encoded {len(parsed_notes)} notes.")