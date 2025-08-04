#!/usr/bin/env bash
# Usage: run_conversion.sh <input.mp3> <lyrics.txt> <output.mp3>
set -eux

INPUT_MP3="$1"
LYRICS_FILE="$2"
OUTPUT_MP3="$3"

# 歌詞ファイルをコピーしてワークディレクトリに配置
cp "$LYRICS_FILE" lyrics.txt

# MP3 を WAV に変換
python - << 'EOF'
from pydub import AudioSegment
AudioSegment.from_mp3('$INPUT_MP3').export('input.wav', format='wav')
EOF

# So-VITS-SVC で歌声変換を実行
python svc/inference.py \
  --config svc/config.json \
  --model_path svc/pretrained_model.pth \
  --input input.wav \
  --lyrics lyrics.txt \
  --output output.wav

# 出力 WAV を MP3 に再変換
python - << 'EOF'
from pydub import AudioSegment
AudioSegment.from_wav('output.wav').export('$OUTPUT_MP3', format='mp3')
EOF
