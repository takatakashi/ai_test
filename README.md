# ai_test

This repository provides a simple Python script for generating WAV files from
Music Macro Language (MML). The script `mml_to_wav.py` reads an MML string and a
sample WAV file and produces a new WAV file with the sequence of notes.

## Usage

```
python3 mml_to_wav.py "T120O5CDEFGAB" sample.wav output.wav
```

The sample WAV should be a mono 16‑bit recording of A4 (440 Hz). The script
resamples this sound to create the other notes. Use `--tempo` to override the
MML tempo if desired.
