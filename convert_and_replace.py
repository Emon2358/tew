import os
import subprocess
from spleeter.separator import Separator
from pydub import AudioSegment
from gtts import gTTS

# --- 設定 ---
INPUT_MP3      = "input.mp3"
TMP_DIR        = "tmp"
SEP_DIR        = os.path.join(TMP_DIR, "separated")
REPLACE_TTS    = os.path.join(TMP_DIR, "tts_nichibasnight.wav")
VC_INPUT       = REPLACE_TTS
VC_OUTPUT      = os.path.join(TMP_DIR, "vc_output.wav")
OUTPUT_FINAL   = "output_nichibasnight.mp3"

# 差し替え範囲（ms）
LYRIC_START_MS = 30000
LYRIC_END_MS   = 50000

os.makedirs(TMP_DIR, exist_ok=True)

# 1) 分離
Separator('spleeter:2stems').separate_to_file(INPUT_MP3, SEP_DIR)
base = os.path.join(SEP_DIR, os.path.splitext(os.path.basename(INPUT_MP3))[0])
acc_path = os.path.join(base, "accompaniment.wav")
voc_path = os.path.join(base, "vocals.wav")

# 2) TTS 生成
tts = gTTS("にちばすないと", lang="ja")
tts.save(REPLACE_TTS)
seg_len = LYRIC_END_MS - LYRIC_START_MS
tts_audio = AudioSegment.from_file(REPLACE_TTS)
combined = AudioSegment.empty()
while len(combined) < seg_len:
    combined += tts_audio
combined[:seg_len].export(REPLACE_TTS, format="wav")

# 3) 声質変換
subprocess.run([
    "python", "inference/inference_main.py",
    "-c", "configs/vc_configs.json",
    "-m", "checkpoints/G_44k.pth",
    "-n", "0",
    "-i", REPLACE_TTS,
    "-o", VC_OUTPUT
], cwd="so-vits-svc")

# 4) 差し替え＆ミックス
accomp = AudioSegment.from_file(acc_path)
vocals = AudioSegment.from_file(voc_path)
vc_seg = AudioSegment.from_file(VC_OUTPUT)
before = vocals[:LYRIC_START_MS]
after  = vocals[LYRIC_END_MS:]
new_vocals = before + vc_seg + after
final = accomp.overlay(new_vocals - 3)
final.export(OUTPUT_FINAL, format="mp3")
print("✅ Completed:", OUTPUT_FINAL)
