import argparse
import mido
import json

def note_number_to_name(note_number):
    """MIDIノート番号を音名に変換"""
    note_name = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    return note_name[note_number % 12] + str(note_number // 12 - 2)

def parse_header(track, tick_per_beat):
    """ヘッダートラックを解析し、テンポと拍子の変化を取得"""
    tempo_data = []
    beat_data = []
    absolute_time = 0.0
    absolute_tick = 0
    current_tempo = 500000  # デフォルト値（120 BPM）
    current_beat_numerator = 4
    current_beat_denominator = 4

    for msg in track:
        # 経過時間を更新
        absolute_time += mido.tick2second(msg.time, tick_per_beat, current_tempo)
        absolute_tick += msg.time
        if msg.type == 'set_tempo':
            current_tempo = msg.tempo
            tempo_data.append({
                "time": round(absolute_time, 5),
                "bpm": mido.tempo2bpm(current_tempo,(current_beat_numerator,current_beat_denominator)),
                "tick":absolute_tick
            })
        elif msg.type == 'time_signature':
            current_beat_numerator = msg.numerator
            current_beat_denominator = msg.denominator
            beat_data.append({
                "time": round(absolute_time, 5),
                "beat": (current_beat_numerator, current_beat_denominator),
                "tick":absolute_tick
            })

    return tempo_data, beat_data

def process_track(track, tick_per_beat, tempo_data, beat_data):
    print(track)
    absolute_time = 0.0
    absolute_tick = 0
    current_tempo = 500000
    tempo_index = 0
    beat_index = 0
    same_time_notes = []
    note_data = []
    CC_data = {}
    pitch_bend_data = []
    lyrics_data = []

    for msg in track:
        absolute_time += mido.tick2second(msg.time, tick_per_beat, current_tempo)
        absolute_tick += msg.time

        while tempo_index < len(tempo_data) - 1 and absolute_time >= tempo_data[tempo_index + 1]["time"]:
            tempo_index += 1
            current_tempo = mido.bpm2tempo(tempo_data[tempo_index]["bpm"],beat_data[beat_index]["beat"])

        while beat_index < len(beat_data) - 1 and absolute_time >= beat_data[beat_index + 1]["time"]:
            beat_index += 1
        
        if msg.time!=0 and same_time_notes!=[]:
            for note in same_time_notes:
                if lyrics_data!=[]:
                    note["text"]=lyrics_data.pop(0)
                else:
                    break
            same_time_notes.clear()

        if msg.type == 'note_on':
            note={
                "time": round(absolute_time, 5),
                "note_length": 0.0,
                "note": note_number_to_name(msg.note),
                "velocity": msg.velocity,
                "text": "",
                "beat_position": (absolute_tick-beat_data[beat_index]["tick"])/tick_per_beat *(beat_data[beat_index]["beat"][1]/4)  % beat_data[beat_index]["beat"][0]+1
            }
            note_data.append(note)
            same_time_notes.append(note)
            
        elif msg.type == 'note_off':
            for note in note_data[::-1]:
                if note["note"] == note_number_to_name(msg.note) and note["note_length"] == 0.0:
                    note["note_length"] = round(absolute_time - note["time"], 5)
                    break
        elif msg.type == 'lyrics':
            lyrics_data.append(msg.text)
        elif msg.type == 'control_change':
            if msg.control not in CC_data:
                CC_data[msg.control] = []
            CC_data[msg.control].append({
                "time": round(absolute_time, 5),
                "value": msg.value
            })
        elif msg.type == 'pitchwheel':
            pitch_bend_data.append({
                "time": round(absolute_time, 5),
                "value": msg.pitch
            })

    return note_data, CC_data, pitch_bend_data

def write_json_file(file_name, data):
    with open(file_name, 'w') as f:
        json.dump(data, f, indent=4)

def main():
    parser = argparse.ArgumentParser(description="MIDIファイルをJSONに変換します。")
    parser.add_argument("midi_file", help="変換するMIDIファイルのパスを指定してください。")
    args = parser.parse_args()

    midi_file = mido.MidiFile(args.midi_file)
    tick_per_beat = midi_file.ticks_per_beat

    # ヘッダートラックの解析
    tempo_data, beat_data = parse_header(midi_file.tracks[0], tick_per_beat)
    header_data = {
        "tempo_data": tempo_data,
        "beat_data": beat_data
    }
    write_json_file(f"header_{midi_file.tracks[0].name}.json", header_data)

    # 各トラックを解析
    for i, track in enumerate(midi_file.tracks[1:], start=1):
        note_data, CC_data, pitch_bend_data = process_track(track, tick_per_beat, tempo_data, beat_data)
        output_data = {
            "note_data": note_data,
            "CC_data": CC_data,
            "pitch_bend_data": pitch_bend_data
        }
        track_name = f"track_{i}" if not track.name else track.name
        write_json_file(f"{track_name}.json", output_data)

if __name__ == "__main__":
    main()