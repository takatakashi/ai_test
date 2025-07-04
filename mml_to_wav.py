import argparse
import wave
import audioop
import math

NOTE_BASE = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}

def parse_mml(mml: str):
    pos = 0
    tempo = 120
    default_length = 4
    octave = 4
    tokens = []
    mml = mml.strip()
    while pos < len(mml):
        ch = mml[pos].upper()
        pos += 1
        if ch in 'CDEFGABR':
            note = ch
            accidental = 0
            length = default_length
            dotted = False
            if note != 'R' and pos < len(mml) and mml[pos] in ('#','+','-'):
                if mml[pos] in ('#','+'):
                    accidental = 1
                else:
                    accidental = -1
                pos += 1
            num=''
            while pos < len(mml) and mml[pos].isdigit():
                num += mml[pos]
                pos +=1
            if num:
                length = int(num)
            if pos < len(mml) and mml[pos]=='.':
                dotted = True
                pos +=1
            tokens.append(('note', note, octave, length, dotted, accidental))
        elif ch == 'O':
            num=''
            while pos < len(mml) and mml[pos].isdigit():
                num += mml[pos]
                pos +=1
            if num:
                octave = int(num)
        elif ch == 'L':
            num=''
            while pos < len(mml) and mml[pos].isdigit():
                num += mml[pos]
                pos +=1
            if num:
                default_length = int(num)
        elif ch == 'T':
            num=''
            while pos < len(mml) and mml[pos].isdigit():
                num += mml[pos]
                pos+=1
            if num:
                tempo=int(num)
        elif ch == '<':
            octave -=1
        elif ch == '>':
            octave +=1
        else:
            # skip spaces or unknown chars
            pass
    return tokens, tempo

def note_freq(note, octave, accidental):
    if note == 'R':
        return 0.0
    semitone = NOTE_BASE[note] + accidental + (octave - 4)*12
    return 440.0 * (2 ** (semitone/12))

def generate_note(sample, sample_rate, width, channels, freq, base_freq, duration):
    frames_needed = int(duration * sample_rate)
    if freq <= 0:
        return b'\x00' * frames_needed * width * channels
    ratio = freq / base_freq
    target_rate = int(sample_rate * ratio)
    resampled, _ = audioop.ratecv(sample, width, channels, sample_rate, target_rate, None)
    # repeat or cut
    required_bytes = frames_needed * width * channels
    if len(resampled) >= required_bytes:
        return resampled[:required_bytes]
    else:
        out = resampled
        while len(out) < required_bytes:
            out += resampled
        return out[:required_bytes]

def main():
    parser = argparse.ArgumentParser(description='Convert MML to WAV using sample.')
    parser.add_argument('mml', help='MML string')
    parser.add_argument('sample', help='wav sample (mono, 16bit, base note A4=440Hz)')
    parser.add_argument('output', help='output wav file')
    parser.add_argument('--tempo', type=int, help='override tempo in BPM')
    args = parser.parse_args()

    with wave.open(args.sample, 'rb') as wf:
        sample_rate = wf.getframerate()
        channels = wf.getnchannels()
        width = wf.getsampwidth()
        sample_data = wf.readframes(wf.getnframes())

    tokens, tempo = parse_mml(args.mml)
    if args.tempo:
        tempo = args.tempo

    beat = 60.0 / tempo

    output_data = b''
    for kind, note, octave, length, dotted, accidental in tokens:
        duration = 4.0 / length * beat
        if dotted:
            duration *= 1.5
        freq = note_freq(note, octave, accidental)
        output_data += generate_note(sample_data, sample_rate, width, channels, freq, 440.0, duration)

    with wave.open(args.output, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(width)
        wf.setframerate(sample_rate)
        wf.writeframes(output_data)

if __name__ == '__main__':
    main()
