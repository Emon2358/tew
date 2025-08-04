#!/usr/bin/env bash
# Usage: run_conversion.sh <input.mp3> <lyrics.txt> <output.mp3>
set -eux

INPUT_MP3="$1"
LYRICS_FILE="$2"
OUTPUT_MP3="$3"

# Prepare working files
cp "$LYRICS_FILE" lyrics.txt

# Convert MP3 to WAV
python - << 'EOF'
from pydub import AudioSegment
AudioSegment.from_mp3('$INPUT_MP3').export('input.wav', format='wav')
EOF

# Run singing voice conversion
python svc/inference.py \
  --config svc/config.json \
  --model_path svc/pretrained_model.pth \
  --input input.wav \
  --lyrics lyrics.txt \
  --output output.wav

# Convert WAV back to MP3
python - << 'EOF'
from pydub import AudioSegment
AudioSegment.from_wav('output.wav').export('$OUTPUT_MP3', format='mp3')
EOF
