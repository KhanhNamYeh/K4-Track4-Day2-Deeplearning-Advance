# Colab Session: compute

## Session Created: 2026-09-23 06:54:45
- Endpoint: `gpu-t4-s-kkb-usw1b0-kwifgopznau8`

## Session Created: 2026-09-23 09:40:43
- Endpoint: `m-s-kkb-use1b1-3mc6b5oyc2syb`

### Execution (2026-09-23 09:41:00)
```python
import os, subprocess, shutil
print(os.cpu_count(), shutil.disk_usage('/content'))
print(subprocess.run(['ffmpeg','-version'],capture_output=True,text=True).stdout.splitlines()[0])
print(os.path.ismount('/content/drive'))

```

**Output**:
```
2 usage(total=115658190848, used=21843816448, free=93797597184)
```

**Output**:
```
ffmpeg version 6.1.1-3ubuntu5 Copyright (c) 2000-2023 the FFmpeg developers
False
```

## Session Created: 2026-09-23 10:02:48
- Endpoint: `m-s-kkb-use4b1-2c9mqunnq4a7h`

### Execution (2026-09-23 10:03:05)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 10:03:38)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 10:04:11)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 10:04:45)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 10:05:19)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 10:05:52)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 10:06:26)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 10:06:59)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 10:07:33)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 10:08:07)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 10:08:40)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 10:09:23)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 10:09:56)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 10:10:29)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 10:11:02)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
MOUNTED
```

### Execution (2026-09-23 10:34:43)
```python
# Chay tren Colab: tach audio 16 kHz mono PCM tu videos/ tren Drive ra audio/ tren Drive.
# Chay nen (nohup) de khong phu thuoc ket noi `colab exec`; log o /content/extract.log.
import subprocess
from pathlib import Path

ROOT = next((p for p in [Path('/content/drive/MyDrive/final aic'),
                         *Path('/content/drive/MyDrive').glob('*/final aic')]
             if (p / 'videos').is_dir()), None)
if ROOT is None:
    raise SystemExit('Khong tim thay "final aic/videos" tren Drive')

VIDEO_DIR = ROOT / 'videos'
AUDIO_DIR = ROOT / 'audio'
AUDIO_DIR.mkdir(exist_ok=True)

script = f'''#!/bin/bash
cd /content
mkdir -p /content/wav_tmp
extract() {{
  v="$1"; name=$(basename "${{v%.*}}")
  out="{AUDIO_DIR}/$name.wav"
  if [ -s "$out" ]; then echo "SKIP $name"; return; fi
  tmp="/content/wav_tmp/$name.wav"
  echo "START $name $(date +%T)"
  if ffmpeg -nostdin -y -loglevel error -i "$v" -vn -acodec pcm_s16le -ar 16000 -ac 1 "$tmp" \\
     && cp "$tmp" "$out.part" && mv "$out.part" "$out"; then
    echo "DONE $name $(date +%T) $(du -h "$out" | cut -f1)"
  else
    echo "FAIL $name"
  fi
  rm -f "$tmp"
}}
export -f extract
ls "{VIDEO_DIR}"/*.mp4 | xargs -P 2 -I{{}} bash -c 'extract "{{}}"'
echo ALL_FINISHED
'''
Path('/content/extract.sh').write_text(script)
print('ROOT =', ROOT)
print('videos:', sorted(p.name for p in VIDEO_DIR.glob('*.mp4')), flush=True)
# Chay chan trong kernel de VM luon BUSY (Colab free thu hoi VM khi kernel ranh).
proc = subprocess.Popen('bash /content/extract.sh 2>&1 | tee /content/extract.log',
                        shell=True, stdout=subprocess.PIPE, text=True)
for line in proc.stdout:
    print(line, end='', flush=True)
proc.wait()

```

**Output**:
```
ROOT = /content/drive/MyDrive/final aic
```

**Output**:
```
videos: ['S01-V001.mp4', 'S01-V002.mp4', 'S01-V003.mp4', 'S01-V004.mp4', 'S01-V005.mp4', 'S01-V006.mp4', 'S01-V007.mp4', 'S01-V008.mp4', 'S01-V009.mp4', 'S01-V010.mp4', 'S01-V011.mp4', 'S01-V012.mp4']
```

**Output**:
```
START S01-V001 10:11:12
```

**Output**:
```
START S01-V002 10:11:12
```

**Output**:
```
DONE S01-V001 10:14:11 304M
```

**Output**:
```
START S01-V003 10:14:11
```

**Output**:
```
DONE S01-V002 10:14:54 310M
```

**Output**:
```
START S01-V004 10:14:54
```

**Output**:
```
DONE S01-V003 10:16:19 268M
```

**Output**:
```
START S01-V005 10:16:19
```

**Output**:
```
DONE S01-V004 10:18:34 433M
```

**Output**:
```
START S01-V006 10:18:35
```

**Output**:
```
DONE S01-V005 10:19:41 434M
```

**Output**:
```
START S01-V007 10:19:41
```

**Output**:
```
DONE S01-V006 10:20:55 297M
```

**Output**:
```
START S01-V008 10:20:55
```

**Output**:
```
DONE S01-V007 10:25:04 618M
```

**Output**:
```
START S01-V009 10:25:04
```

**Output**:
```
DONE S01-V008 10:25:38 528M
```

**Output**:
```
START S01-V010 10:25:38
```

**Output**:
```
DONE S01-V009 10:28:09 409M
```

**Output**:
```
START S01-V011 10:28:09
```

**Output**:
```
DONE S01-V010 10:29:25 466M
```

**Output**:
```
START S01-V012 10:29:26
```

**Output**:
```
DONE S01-V011 10:32:57 514M
```

**Output**:
```
DONE S01-V012 10:34:44 544M
```

**Output**:
```
ALL_FINISHED
```

### Execution (2026-09-23 10:35:33)
```python
import subprocess, wave
from pathlib import Path
R=Path('/content/drive/MyDrive/final aic')
bad=0
for v in sorted((R/'videos').glob('*.mp4')):
    w=R/'audio'/(v.stem+'.wav')
    dv=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(v)],capture_output=True,text=True).stdout)
    if not w.exists(): print('MISSING',w.name); bad+=1; continue
    with wave.open(str(w)) as f: dw=f.getnframes()/f.getframerate(); fmt=(f.getframerate(),f.getnchannels(),f.getsampwidth())
    ok=abs(dv-dw)<2
    bad+= not ok
    print(f'{w.name} video={dv:.1f}s wav={dw:.1f}s fmt={fmt} {"OK" if ok else "MISMATCH"}')
print('BAD',bad, 'extra files:', [p.name for p in (R/'audio').iterdir() if p.suffix!='.wav'])

```

**Output**:
```
S01-V001.wav video=9930.1s wav=9930.1s fmt=(16000, 1, 2) OK
```

**Output**:
```
S01-V002.wav video=10155.2s wav=10155.2s fmt=(16000, 1, 2) OK
```

**Output**:
```
S01-V003.wav video=8765.1s wav=8765.1s fmt=(16000, 1, 2) OK
```

**Output**:
```
S01-V004.wav video=14180.1s wav=14180.1s fmt=(16000, 1, 2) OK
```

**Output**:
```
S01-V005.wav video=14191.3s wav=14191.3s fmt=(16000, 1, 2) OK
```

**Output**:
```
S01-V006.wav video=9725.1s wav=9725.1s fmt=(16000, 1, 2) OK
```

**Output**:
```
S01-V007.wav video=20246.2s wav=20246.2s fmt=(16000, 1, 2) OK
```

**Output**:
```
S01-V008.wav video=17284.6s wav=17284.6s fmt=(16000, 1, 2) OK
```

**Output**:
```
S01-V009.wav video=13376.3s wav=13376.3s fmt=(16000, 1, 2) OK
```

**Output**:
```
S01-V010.wav video=15265.1s wav=15265.1s fmt=(16000, 1, 2) OK
```

**Output**:
```
S01-V011.wav video=16840.2s wav=16840.2s fmt=(16000, 1, 2) OK
```

**Output**:
```
S01-V012.wav video=17795.1s wav=17795.1s fmt=(16000, 1, 2) OK
BAD 0 extra files: []
```

## Session Created: 2026-09-23 10:57:54
- Endpoint: `gpu-t4-s-kkb-use1c1-2ngcjxxyrr2h9`

### Execution (2026-09-23 10:59:17)
```python
import subprocess, sys
print(subprocess.run(['nvidia-smi','--query-gpu=name,memory.total','--format=csv'],capture_output=True,text=True).stdout)
r = subprocess.run([sys.executable,'-m','pip','install','-q','faster-whisper'],capture_output=True,text=True)
print('pip rc', r.returncode, r.stderr[-800:])
from faster_whisper import WhisperModel
import time; t=time.time()
model = WhisperModel('kiendt/PhoWhisper-large-ct2', device='cuda', compute_type='float16')
print('model loaded in %.0fs' % (time.time()-t))

```

**Output**:
```
name, memory.total [MiB]
Tesla T4, 15360 MiB

```

**Output**:
```
pip rc 0 
```

**Output**:
```
/usr/local/lib/python3.13/dist-packages/huggingface_hub/utils/_auth.py:138: UserWarning: 
Error while fetching `HF_TOKEN` secret value from your vault: 'Requesting secret HF_TOKEN timed out. Secrets can only be fetched when running from the Colab UI.'.
  warnings.warn(f"\nError while fetching `HF_TOKEN` secret value from your vault: '{str(e)}'.")
```

**Output**:
```
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
```

**Output**:
```
WARNING:huggingface_hub.utils._http:Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
```

**Output**:
```
model loaded in 42s
```

### Execution (2026-09-23 10:59:30)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:00:08)
```python
import faster_whisper, inspect
from faster_whisper import transcribe as T
from faster_whisper.vad import collect_chunks
print(faster_whisper.__version__)
print(inspect.getsource(collect_chunks))
src = inspect.getsource(T.BatchedInferencePipeline)
i = src.find('def forward'); print(src[i:i+2500])
i = src.find('def generate_segment_batched'); print(src[i:i+400])
i = src.find('if not vad_filter'); print(src[i-200:i+2200])

```

**Output**:
```
1.2.1
def collect_chunks(
    audio: np.ndarray,
    chunks: List[dict],
    sampling_rate: int = 16000,
    max_duration: float = float("inf"),
) -> Tuple[List[np.ndarray], List[Dict[str, float]]]:
    """This function merges the chunks of audio into chunks of max_duration (s) length."""
    if not chunks:
        chunk_metadata = {
            "offset": 0,
            "duration": 0,
            "segments": [],
        }
        return [np.array([], dtype=np.float32)], [chunk_metadata]

    audio_chunks = []
    chunks_metadata = []

    current_segments = []
    current_duration = 0
    total_duration = 0
    current_audio = np.array([], dtype=np.float32)

    for chunk in chunks:
        if (
            current_duration + chunk["end"] - chunk["start"]
            > max_duration * sampling_rate
        ):
            audio_chunks.append(current_audio)
            chunk_metadata = {
                "offset": total_duration / sampling_rate,
                "duration": current_duration / sampling_rate,
                "segments": current_segments,
            }
            total_duration += current_duration
            chunks_metadata.append(chunk_metadata)

            current_segments = []

            current_audio = audio[chunk["start"] : chunk["end"]]
            current_duration = chunk["end"] - chunk["start"]
        else:
            current_segments.append(chunk)
            current_audio = np.concatenate(
                (current_audio, audio[chunk["start"] : chunk["end"]])
            )

            current_duration += chunk["end"] - chunk["start"]

    audio_chunks.append(current_audio)

    chunk_metadata = {
        "offset": total_duration / sampling_rate,
        "duration": current_duration / sampling_rate,
        "segments": current_segments,
    }
    chunks_metadata.append(chunk_metadata)
    return audio_chunks, chunks_metadata

def forward(self, features, tokenizer, chunks_metadata, options):
        encoder_output, outputs = self.generate_segment_batched(
            features, tokenizer, options
        )

        segmented_outputs = []
        segment_sizes = []
        for chunk_metadata, output in zip(chunks_metadata, outputs):
            duration = chunk_metadata["duration"]
            segment_size = int(ceil(duration) * self.model.frames_per_second)
            segment_sizes.append(segment_size)
            (
                subsegments,
                seek,
                single_timestamp_ending,
            ) = self.model._split_segments_by_timestamps(
                tokenizer=tokenizer,
                tokens=output["tokens"],
                time_offset=chunk_metadata["offset"],
                segment_size=segment_size,
                segment_duration=duration,
                seek=0,
            )
            segmented_outputs.append(
                [
                    dict(
                        text=tokenizer.decode(subsegment["tokens"]),
                        avg_logprob=output["avg_logprob"],
                        no_speech_prob=output["no_speech_prob"],
                        tokens=subsegment["tokens"],
                        start=subsegment["start"],
                        end=subsegment["end"],
                        compression_ratio=get_compression_ratio(
                            tokenizer.decode(subsegment["tokens"])
                        ),
                        seek=int(
                            chunk_metadata["offset"] * self.model.frames_per_second
                        ),
                    )
                    for subsegment in subsegments
                ]
            )
        if options.word_timestamps:
            self.last_speech_timestamp = self.model.add_word_timestamps(
                segmented_outputs,
                tokenizer,
                encoder_output,
                segment_sizes,
                options.prepend_punctuations,
                options.append_punctuations,
                self.last_speech_timestamp,
            )

        return segmented_outputs

    def generate_segment_batched(
        self,
        features: np.ndarray,
        tokenizer: Tokenizer,
        options: TranscriptionOptions,
    ):
        batch_size = features.shape[0]

        prompt = self.model.get_prompt(
            tokenizer,
            previous_tokens=(
                tokenizer.encode(options.initial_prompt)
def generate_segment_batched(
        self,
        features: np.ndarray,
        tokenizer: Tokenizer,
        options: TranscriptionOptions,
    ):
        batch_size = features.shape[0]

        prompt = self.model.get_prompt(
            tokenizer,
            previous_tokens=(
                tokenizer.encode(options.initial_prompt)
                if options.initial_prompt is not None
      

```

### Execution (2026-09-23 11:00:31)
```python
import inspect
from faster_whisper import transcribe as T
src = inspect.getsource(T.BatchedInferencePipeline.transcribe)
i = src.find('if vad_filter'); print(src[i-300:])
print(inspect.getsource(T.BatchedInferencePipeline._batched_segments_generator))

```

**Output**:
```
er.info(
            "Processing audio with duration %s", format_timestamp(duration)
        )

        chunk_length = chunk_length or self.model.feature_extractor.chunk_length
        # if no segment split is provided, use vad_model and generate segments
        if not clip_timestamps:
            if vad_filter:
                if vad_parameters is None:
                    vad_parameters = VadOptions(
                        max_speech_duration_s=chunk_length,
                        min_silence_duration_ms=160,
                    )
                elif isinstance(vad_parameters, dict):
                    if "max_speech_duration_s" in vad_parameters.keys():
                        vad_parameters.pop("max_speech_duration_s")

                    vad_parameters = VadOptions(
                        **vad_parameters, max_speech_duration_s=chunk_length
                    )

                clip_timestamps = get_speech_timestamps(audio, vad_parameters)
            # run the audio if it is less than 30 sec even without clip_timestamps
            elif duration < chunk_length:
                clip_timestamps = [{"start": 0, "end": audio.shape[0]}]
            else:
                raise RuntimeError(
                    "No clip timestamps found. "
                    "Set 'vad_filter' to True or provide 'clip_timestamps'."
                )

            clip_timestamps_provided = False
            audio_chunks, chunks_metadata = collect_chunks(
                audio, clip_timestamps, max_duration=chunk_length
            )

        else:
            clip_timestamps_provided = True
            clip_timestamps = [
                {k: int(v * sampling_rate) for k, v in segment.items()}
                for segment in clip_timestamps
            ]

            audio_chunks, chunks_metadata = [], []
            for i, clip in enumerate(clip_timestamps):
                audio_chunks.append(audio[clip["start"] : clip["end"]])

                clip_duration = (clip["end"] - clip["start"]) / sampling_rate
                if clip_duration > 30:
                    self.model.logger.warning(
                        "Segment %d is longer than 30 seconds, "
                        "only the first 30 seconds will be transcribed",
                        i,
                    )

                chunks_metadata.append(
                    {
                        "offset": clip["start"] / sampling_rate,
                        "duration": clip_duration,
                        "segments": [clip],
                    }
                )

        duration_after_vad = (
            sum((segment["end"] - segment["start"]) for segment in clip_timestamps)
            / sampling_rate
        )

        self.model.logger.info(
            "VAD filter removed %s of audio",
            format_timestamp(duration - duration_after_vad),
        )

        features = (
            [self.model.feature_extractor(chunk)[..., :-1] for chunk in audio_chunks]
            if duration_after_vad
            else []
        )

        all_language_probs = None
        # detecting the language if not provided
        if language is None:
            if not self.model.model.is_multilingual:
                language = "en"
                language_probability = 1
            else:
                (
                    language,
                    language_probability,
                    all_language_probs,
                ) = self.model.detect_language(
                    features=np.concatenate(
                        features
                        + [
                            np.full((self.model.model.n_mels, 1), -1.5, dtype="float32")
                        ],
                        axis=1,
                    ),  # add a dummy feature to account for empty audio
                    language_detection_segments=language_detection_segments,
                    language_detection_threshold=language_detection_threshold,
                )

                self.model.logger.info(
                    "Detected language '%s' with probability %.2f",
                    language,
                    language_probability,
                )
        else:
            if not self.model.model.is_multilingual and language != "en":
                self.model.logger.warning(
                    "The current model is English-only but the language parameter is set to '%s'; "
                    "using 'en' instead." % language
                )
                language = "en"

            language_probability = 1

        tokenizer = Tokenizer(
            self.model.hf_tokenizer,
            self.model.model.is_multilingual,
            task=task,
            language=language,
        )

        features = (
            np.stack([pad_or_trim(feature) for feature in features]) if features else []
        )

        options = TranscriptionOptions(
            beam_size=beam_size,
            best_of=best_of,
            patience=patience,
            length_penalty=length_penalty,
            repetition_penalty=repetition_penalty,
            no_repeat_ngram_size=no_repeat_ngram_size,
            log_prob_threshold=log_prob_threshold,
            no_speech_threshold=no_speech_threshold,
            compression_ratio_threshold=compression_ratio_threshold,
            temperatures=(
                temperature[:1]
                if isinstance(temperature, (list, tuple))
                else [temperature]
            ),
            initial_prompt=initial_prompt,
            prefix=prefix,
            suppress_blank=suppress_blank,
            suppress_tokens=(
                get_suppressed_tokens(tokenizer, suppress_tokens)
                if suppress_tokens
                else suppress_tokens
            ),
            prepend_punctuations=prepend_punctuations,
            append_punctuations=append_punctuations,
            max_new_tokens=max_new_tokens,
            hotwords=hotwords,
            word_timestamps=word_timestamps,
            hallucination_silence_threshold=None,
            condition_on_previous_text=False,
            clip_timestamps=clip_timestamps,
            prompt_reset_on_temperature=0.5,
            multilingual=multilingual,
            without_timestamps=without_timestamps,
            max_initial_timestamp=0.0,
        )

        info = TranscriptionInfo(
            language=language,
            language_probability=language_probability,
            duration=duration,
            duration_after_vad=duration_after_vad,
            transcription_options=options,
            vad_options=vad_parameters,
            all_language_probs=all_language_probs,
        )

        segments = self._batched_segments_generator(
            features,
            tokenizer,
            chunks_metadata,
            batch_size,
            options,
            log_progress,
        )
        if not clip_timestamps_provided:
            segments = restore_speech_timestamps(
                segments, clip_timestamps, sampling_rate
            )

        return segments, info

    def _batched_segments_generator(
        self, features, tokenizer, chunks_metadata, batch_size, options, log_progress
    ):
        pbar = tqdm(total=len(features), disable=not log_progress, position=0)
        seg_idx = 0
        for i in range(0, len(features), batch_size):
            results = self.forward(
                features[i : i + batch_size],
                tokenizer,
                chunks_metadata[i : i + batch_size],
                options,
            )

            for result in results:
                for segment in result:
                    seg_idx += 1
                    yield Segment(
                        seek=segment["seek"],
                        id=seg_idx,
                        text=segment["text"],
                        start=round(segment["start"], 3),
                        end=round(segment["end"], 3),
                        words=(
                            None
                            if not options.word_timestamps
                            else [Word(**word) for word in segment["words"]]
                        ),
                        tokens=segment["tokens"],
                        avg_logprob=segment["avg_logprob"],
                        no_speech_prob=segment["no_speech_prob"],
                        compression_ratio=segment["compression_ratio"],
                        temperature=options.temperatures[0],
                    )

                pbar.update(1)

        pbar.close()
        self.last_speech_timestamp = 0.0

```

### Execution (2026-09-23 11:01:28)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:02:01)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:02:33)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:03:06)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:03:39)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:04:13)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:04:47)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:05:27)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:06:01)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:06:33)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:07:07)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:07:41)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:08:13)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:08:47)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:09:21)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:09:54)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:10:28)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:11:00)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:11:34)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:12:07)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:12:41)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:13:14)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:13:48)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:14:21)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:14:55)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:15:30)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:16:03)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:16:37)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:17:10)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:17:44)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:18:17)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:18:50)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:19:23)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:19:56)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:20:30)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:21:03)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:21:37)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:22:11)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:22:44)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:23:18)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:23:51)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:24:25)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:24:59)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:25:33)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:26:05)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:26:39)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:27:12)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:27:45)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:28:20)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:28:53)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:29:26)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:29:59)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:30:32)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:31:06)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:31:39)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:32:13)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:32:45)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:33:36)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:34:09)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:34:43)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:35:15)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:35:48)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:36:23)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:36:56)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:37:29)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:38:03)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:38:36)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:39:10)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:39:43)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:40:19)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:40:52)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:41:25)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:41:59)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:42:33)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:43:06)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:43:39)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 11:44:05)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
MOUNTED
```

### Execution (2026-09-23 11:44:11)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
MOUNTED
```

### Execution (2026-09-23 11:44:32)
```python
# Chay tren Colab T4: WAV (final aic/audio) -> transcript JSON (final aic/transcripts).
# Giu nguyen logic src_aic26/voice_2_text.ipynb (VAD cung tham so, 1 doan VAD = 1 ban ghi,
# loc hallucination) nhung giai ma THEO LO tren GPU:
#   - doan VAD <= 30s: BatchedInferencePipeline voi clip_timestamps (moi doan la 1 muc
#     trong lo, KHONG bi gop nhu collect_chunks, offset tuyet doi)
#   - doan > 30s: model.transcribe tuan tu nhu notebook goc (lo se cat mat phan sau 30s)
import bisect, json, shutil, sys, time
from pathlib import Path

import torch  # chi de doc bo nho GPU
from faster_whisper import BatchedInferencePipeline, WhisperModel
from faster_whisper.audio import decode_audio
from faster_whisper.vad import VadOptions, get_speech_timestamps

ROOT = Path('/content/drive/MyDrive/final aic')
IN_DIR, OUT_DIR = ROOT / 'audio', ROOT / 'transcripts'
OUT_DIR.mkdir(exist_ok=True)
SR = 16000
LANG = 'vi'
DECODE = dict(language=LANG, temperature=0, beam_size=5, word_timestamps=False,
              without_timestamps=False)
BATCH_CANDIDATES = [64, 48, 32, 16, 8]


def _is_hallucination(seg, max_chars_per_sec=80, max_repeat_count=6):
    duration = seg["end"] - seg["start"]
    text = seg["text"]
    if duration <= 0:
        return True
    if len(text) / duration > max_chars_per_sec:
        return True
    words = text.split()
    for n in (2, 3):
        for i in range(len(words) - n + 1):
            phrase = " ".join(words[i: i + n])
            if len(phrase) < 5:
                continue
            if text.count(phrase) >= max_repeat_count:
                return True
    return False


def vad_chunks(audio):
    opts = VadOptions(min_silence_duration_ms=300, speech_pad_ms=50, min_speech_duration_ms=1000)
    return get_speech_timestamps(audio, opts, SR)


def texts_sequential(model, audio, chunks):
    """Duong goc cua notebook: 1 lan transcribe cho moi doan."""
    out = []
    for c in chunks:
        segs, _ = model.transcribe(audio[c["start"]:c["end"]], vad_filter=False,
                                   condition_on_previous_text=True, **DECODE)
        out.append(" ".join(t for t in (s.text.strip() for s in segs) if t))
    return out


def texts_batched(pipe, audio, chunks, batch_size):
    """Moi doan (<=30s) la 1 clip; gom text cua cac segment tra ve theo doan cha."""
    clips = [{"start": c["start"] / SR, "end": c["end"] / SR} for c in chunks]
    starts = [int(c["start"] / SR * 100) for c in chunks]  # seek = offset * 100 fps
    parts = [[] for _ in chunks]
    segs, _ = pipe.transcribe(audio, clip_timestamps=clips, batch_size=batch_size,
                              vad_filter=False, **DECODE)
    for s in segs:
        # Tuong duong nguong bo doan im lang cua transcribe tuan tu
        if s.no_speech_prob > 0.6 and s.avg_logprob < -1.0:
            continue
        idx = bisect.bisect_right(starts, s.seek + 1) - 1
        t = s.text.strip()
        if t:
            parts[idx].append(t)
    return [" ".join(p) for p in parts]


def transcribe_file(model, pipe, path, batch_size):
    audio = decode_audio(str(path), sampling_rate=SR)
    chunks = vad_chunks(audio)
    short = [i for i, c in enumerate(chunks) if (c["end"] - c["start"]) / SR <= 30]
    long_ = [i for i, c in enumerate(chunks) if (c["end"] - c["start"]) / SR > 30]
    texts = [""] * len(chunks)
    for i, t in zip(short, texts_batched(pipe, audio, [chunks[i] for i in short], batch_size)):
        texts[i] = t
    for i, t in zip(long_, texts_sequential(model, audio, [chunks[i] for i in long_])):
        texts[i] = t
    result = []
    for c, text in zip(chunks, texts):
        if text:
            seg = {"start": round(c["start"] / SR, 2), "end": round(c["end"] / SR, 2), "text": text}
            if not _is_hallucination(seg):
                result.append(seg)
    return result, len(chunks), len(long_)


def pick_batch_size(model, pipe, audio, chunks):
    """Do toc do tren cung 1 mau; lay batch lon nhat khong OOM va nhanh nhat."""
    sample = [c for c in chunks if (c["end"] - c["start"]) / SR <= 30][:192]
    best, best_rate = None, 0
    for bs in BATCH_CANDIDATES:
        try:
            torch.cuda.reset_peak_memory_stats()
            t = time.time()
            texts_batched(pipe, audio, sample, bs)
            dt = time.time() - t
        except Exception as ex:  # OOM tu CTranslate2 la RuntimeError
            print(f'  batch {bs}: loi {type(ex).__name__}: {str(ex)[:120]}', flush=True)
            continue
        rate = len(sample) / dt
        print(f'  batch {bs}: {rate:.1f} doan/s', flush=True)
        if rate > best_rate:
            best, best_rate = bs, rate
    return best, sample


def compare_with_notebook(model, pipe, audio, sample, bs, n=40):
    """Kiem tra chat luong: so text cua lo voi duong tuan tu goc tren n doan."""
    import difflib
    a = texts_sequential(model, audio, sample[:n])
    b = texts_batched(pipe, audio, sample[:n], bs)
    same = sum(x == y for x, y in zip(a, b))
    sim = sum(difflib.SequenceMatcher(None, x, y).ratio() for x, y in zip(a, b)) / n
    print(f'  so voi notebook goc tren {n} doan: trung khop {same}/{n}, do giong TB {sim:.3f}', flush=True)
    for x, y in zip(a, b):
        if x != y:
            print(f'    goc : {x[:150]}\n    lo  : {y[:150]}', flush=True)
            break


model = WhisperModel('kiendt/PhoWhisper-large-ct2', device='cuda', compute_type='float16')
pipe = BatchedInferencePipeline(model=model)
wavs = sorted(IN_DIR.glob('*.wav'))
print(f'{len(wavs)} wav', flush=True)

batch_size = int(sys.argv[1]) if len(sys.argv) > 1 else None
for wav in wavs:
    out = OUT_DIR / f'{wav.stem}.json'
    if out.exists() and out.stat().st_size > 0:
        print('SKIP', wav.stem, flush=True)
        continue
    t = time.time()
    try:
        local = Path('/content') / wav.name  # doc tu dia VM thay vi Drive FUSE
        shutil.copy(wav, local)
        if batch_size is None:
            audio = decode_audio(str(local), sampling_rate=SR)
            batch_size, sample = pick_batch_size(model, pipe, audio, vad_chunks(audio))
            print(f'BATCH_SIZE = {batch_size}', flush=True)
            compare_with_notebook(model, pipe, audio, sample, batch_size)
            del audio
        segs, n_chunks, n_long = transcribe_file(model, pipe, local, batch_size)
        local.unlink()
        tmp = Path('/content') / out.name
        tmp.write_text(json.dumps(segs, ensure_ascii=False, indent=2), encoding='utf-8')
        shutil.copy(tmp, out)
        print(f'DONE {wav.stem} {len(segs)}/{n_chunks} doan ({n_long} doan >30s) '
              f'{time.time()-t:.0f}s {time.strftime("%H:%M:%S")}', flush=True)
    except Exception as ex:
        print(f'FAIL {wav.stem} {ex!r}', flush=True)
print('ALL_FINISHED', flush=True)

```

**Output**:
```
12 wav
```

*File Operation*: `download` on `/content/gpu.txt`

*File Operation*: `download` on `/content/g2.txt`

## Session Created: 2026-09-23 15:18:23
- Endpoint: `gpu-t4-s-kkb-usw4a0-2ewgmk34e5yma`

### Execution (2026-09-23 15:19:32)
```python
import subprocess, sys
print(subprocess.run(['nvidia-smi','--query-gpu=name,memory.total','--format=csv'],capture_output=True,text=True).stdout)
r = subprocess.run([sys.executable,'-m','pip','install','-q','faster-whisper'],capture_output=True,text=True)
print('pip rc', r.returncode, r.stderr[-800:])
from faster_whisper import WhisperModel
import time; t=time.time()
model = WhisperModel('kiendt/PhoWhisper-large-ct2', device='cuda', compute_type='float16')
print('model loaded in %.0fs' % (time.time()-t))

```

**Output**:
```
name, memory.total [MiB]
Tesla T4, 15360 MiB

```

**Output**:
```
pip rc 0 
```

**Output**:
```
/usr/local/lib/python3.13/dist-packages/huggingface_hub/utils/_auth.py:138: UserWarning: 
Error while fetching `HF_TOKEN` secret value from your vault: 'Requesting secret HF_TOKEN timed out. Secrets can only be fetched when running from the Colab UI.'.
  warnings.warn(f"\nError while fetching `HF_TOKEN` secret value from your vault: '{str(e)}'.")
```

**Output**:
```
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
```

**Output**:
```
WARNING:huggingface_hub.utils._http:Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
```

**Output**:
```
model loaded in 41s
```

### Execution (2026-09-23 15:19:36)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 15:20:08)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 15:20:41)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 15:21:14)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 15:21:47)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 15:22:21)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 15:22:53)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 15:23:27)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 15:24:00)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 15:24:32)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 15:25:05)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 15:25:38)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 15:26:10)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 15:26:43)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 15:27:26)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 15:27:59)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 15:28:32)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 15:29:42)
```python
import os
from pathlib import Path
print('mounted', os.path.isdir('/content/drive/MyDrive'))
R = Path('/content/drive/MyDrive/final aic')
print('root', R.exists())
if R.exists():
    for d in ['audio', 'transcripts']:
        print(d, sorted(p.name for p in (R/d).iterdir()) if (R/d).exists() else 'MISSING')
    t = R/'transcripts'/'_write_test.tmp'
    try: t.write_text('x'); t.unlink(); print('write OK')
    except Exception as e: print('write FAIL', e)
else:
    print(sorted(os.listdir('/content/drive/MyDrive'))[:30] if os.path.isdir('/content/drive/MyDrive') else '')

```

**Output**:
```
mounted False
root False

```

### Execution (2026-09-23 15:29:54)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 15:30:27)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 15:31:10)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 15:31:44)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 15:32:16)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 15:32:49)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-23 15:33:21)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
MOUNTED
```

### Execution (2026-09-23 15:33:24)
```python
import os
from pathlib import Path
print('mounted', os.path.isdir('/content/drive/MyDrive'))
R = Path('/content/drive/MyDrive/final aic')
print('root', R.exists())
if R.exists():
    for d in ['audio', 'transcripts']:
        print(d, sorted(p.name for p in (R/d).iterdir()) if (R/d).exists() else 'MISSING')
    t = R/'transcripts'/'_write_test.tmp'
    try: t.write_text('x'); t.unlink(); print('write OK')
    except Exception as e: print('write FAIL', e)
else:
    print(sorted(os.listdir('/content/drive/MyDrive'))[:30] if os.path.isdir('/content/drive/MyDrive') else '')

```

**Output**:
```
mounted True
```

**Output**:
```
root False
['BI_Project', 'Blueprint_He_thong_AI_Agent_UAV.pdf', 'Classroom', 'Colab Notebooks', 'DSSV - Phân công chào cờ HK2 năm học 2024 - 2025.xlsx', 'HOADON_0301394608_2K25TDV_631624.xml', 'HOADON_0301394608_2K25TDV_657778.xml', 'HOADON_0301394608_2K25TDV_672379.xml', 'HOADON_0301394608_2K25TDV_687958.xml', 'HOADON_0301394608_2K25TDV_704267.xml', 'HOADON_0301394608_2K25TDV_736409.xml', 'Screencast from 2026-05-07 13-19-37.webm', 'Summer Notes.gsheet', 'Untitled', 'Untitled (1)', 'note.gdoc', 'tạo bảng theo chiều ngang dịch qua tiếng việt cho....gsheet']
```

### Execution (2026-09-23 15:33:31)
```python
# Chay tren Colab T4: WAV (final aic/audio) -> transcript JSON (final aic/transcripts).
# Giu nguyen logic src_aic26/voice_2_text.ipynb (VAD cung tham so, 1 doan VAD = 1 ban ghi,
# loc hallucination) nhung giai ma THEO LO tren GPU:
#   - doan VAD <= 30s: BatchedInferencePipeline voi clip_timestamps (moi doan la 1 muc
#     trong lo, KHONG bi gop nhu collect_chunks, offset tuyet doi)
#   - doan > 30s: model.transcribe tuan tu nhu notebook goc (lo se cat mat phan sau 30s)
import bisect, json, shutil, sys, time
from pathlib import Path

import torch  # chi de doc bo nho GPU
from faster_whisper import BatchedInferencePipeline, WhisperModel
from faster_whisper.audio import decode_audio
from faster_whisper.vad import VadOptions, get_speech_timestamps

ROOT = Path('/content/drive/MyDrive/final aic')
IN_DIR, OUT_DIR = ROOT / 'audio', ROOT / 'transcripts'
OUT_DIR.mkdir(exist_ok=True)
SR = 16000
LANG = 'vi'
DECODE = dict(language=LANG, temperature=0, beam_size=5, word_timestamps=False,
              without_timestamps=False)
BATCH_CANDIDATES = [64, 48, 32, 16, 8]


def _is_hallucination(seg, max_chars_per_sec=80, max_repeat_count=6):
    duration = seg["end"] - seg["start"]
    text = seg["text"]
    if duration <= 0:
        return True
    if len(text) / duration > max_chars_per_sec:
        return True
    words = text.split()
    for n in (2, 3):
        for i in range(len(words) - n + 1):
            phrase = " ".join(words[i: i + n])
            if len(phrase) < 5:
                continue
            if text.count(phrase) >= max_repeat_count:
                return True
    return False


def vad_chunks(audio):
    opts = VadOptions(min_silence_duration_ms=300, speech_pad_ms=50, min_speech_duration_ms=1000)
    return get_speech_timestamps(audio, opts, SR)


def texts_sequential(model, audio, chunks):
    """Duong goc cua notebook: 1 lan transcribe cho moi doan."""
    out = []
    for c in chunks:
        segs, _ = model.transcribe(audio[c["start"]:c["end"]], vad_filter=False,
                                   condition_on_previous_text=True, **DECODE)
        out.append(" ".join(t for t in (s.text.strip() for s in segs) if t))
    return out


def texts_batched(pipe, audio, chunks, batch_size):
    """Moi doan (<=30s) la 1 clip; gom text cua cac segment tra ve theo doan cha."""
    clips = [{"start": c["start"] / SR, "end": c["end"] / SR} for c in chunks]
    starts = [int(c["start"] / SR * 100) for c in chunks]  # seek = offset * 100 fps
    parts = [[] for _ in chunks]
    segs, _ = pipe.transcribe(audio, clip_timestamps=clips, batch_size=batch_size,
                              vad_filter=False, **DECODE)
    for s in segs:
        # Tuong duong nguong bo doan im lang cua transcribe tuan tu
        if s.no_speech_prob > 0.6 and s.avg_logprob < -1.0:
            continue
        idx = bisect.bisect_right(starts, s.seek + 1) - 1
        t = s.text.strip()
        if t:
            parts[idx].append(t)
    return [" ".join(p) for p in parts]


def transcribe_file(model, pipe, path, batch_size):
    audio = decode_audio(str(path), sampling_rate=SR)
    chunks = vad_chunks(audio)
    short = [i for i, c in enumerate(chunks) if (c["end"] - c["start"]) / SR <= 30]
    long_ = [i for i, c in enumerate(chunks) if (c["end"] - c["start"]) / SR > 30]
    texts = [""] * len(chunks)
    for i, t in zip(short, texts_batched(pipe, audio, [chunks[i] for i in short], batch_size)):
        texts[i] = t
    for i, t in zip(long_, texts_sequential(model, audio, [chunks[i] for i in long_])):
        texts[i] = t
    result = []
    for c, text in zip(chunks, texts):
        if text:
            seg = {"start": round(c["start"] / SR, 2), "end": round(c["end"] / SR, 2), "text": text}
            if not _is_hallucination(seg):
                result.append(seg)
    return result, len(chunks), len(long_)


def pick_batch_size(model, pipe, audio, chunks):
    """Do toc do tren cung 1 mau; lay batch lon nhat khong OOM va nhanh nhat."""
    sample = [c for c in chunks if (c["end"] - c["start"]) / SR <= 30][:192]
    best, best_rate = None, 0
    for bs in BATCH_CANDIDATES:
        try:
            torch.cuda.reset_peak_memory_stats()
            t = time.time()
            texts_batched(pipe, audio, sample, bs)
            dt = time.time() - t
        except Exception as ex:  # OOM tu CTranslate2 la RuntimeError
            print(f'  batch {bs}: loi {type(ex).__name__}: {str(ex)[:120]}', flush=True)
            continue
        rate = len(sample) / dt
        print(f'  batch {bs}: {rate:.1f} doan/s', flush=True)
        if rate > best_rate:
            best, best_rate = bs, rate
    return best, sample


def compare_with_notebook(model, pipe, audio, sample, bs, n=40):
    """Kiem tra chat luong: so text cua lo voi duong tuan tu goc tren n doan."""
    import difflib
    a = texts_sequential(model, audio, sample[:n])
    b = texts_batched(pipe, audio, sample[:n], bs)
    same = sum(x == y for x, y in zip(a, b))
    sim = sum(difflib.SequenceMatcher(None, x, y).ratio() for x, y in zip(a, b)) / n
    print(f'  so voi notebook goc tren {n} doan: trung khop {same}/{n}, do giong TB {sim:.3f}', flush=True)
    for x, y in zip(a, b):
        if x != y:
            print(f'    goc : {x[:150]}\n    lo  : {y[:150]}', flush=True)
            break


model = WhisperModel('kiendt/PhoWhisper-large-ct2', device='cuda', compute_type='float16')
pipe = BatchedInferencePipeline(model=model)
wavs = sorted(IN_DIR.glob('*.wav'))
print(f'{len(wavs)} wav', flush=True)

# Da do tren T4 (2026-09-23): 8/16/32 cung ~1.3 doan/s (GPU 100%), 48/64 OOM.
batch_size = 8
for wav in wavs:
    out = OUT_DIR / f'{wav.stem}.json'
    if out.exists() and out.stat().st_size > 0:
        print('SKIP', wav.stem, flush=True)
        continue
    t = time.time()
    try:
        local = Path('/content') / wav.name  # doc tu dia VM thay vi Drive FUSE
        shutil.copy(wav, local)
        if batch_size is None:
            audio = decode_audio(str(local), sampling_rate=SR)
            batch_size, sample = pick_batch_size(model, pipe, audio, vad_chunks(audio))
            print(f'BATCH_SIZE = {batch_size}', flush=True)
            compare_with_notebook(model, pipe, audio, sample, batch_size)
            del audio
        segs, n_chunks, n_long = transcribe_file(model, pipe, local, batch_size)
        local.unlink()
        tmp = Path('/content') / out.name
        tmp.write_text(json.dumps(segs, ensure_ascii=False, indent=2), encoding='utf-8')
        shutil.copy(tmp, out)
        print(f'DONE {wav.stem} {len(segs)}/{n_chunks} doan ({n_long} doan >30s) '
              f'{time.time()-t:.0f}s {time.strftime("%H:%M:%S")}', flush=True)
    except Exception as ex:
        print(f'FAIL {wav.stem} {ex!r}', flush=True)
print('ALL_FINISHED', flush=True)

```

### Execution (2026-09-23 15:33:50)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:34:22)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:34:55)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:35:28)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:36:01)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:36:33)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:37:06)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:37:39)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:38:22)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:38:55)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:39:27)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:40:00)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:40:33)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:41:05)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:41:39)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:42:12)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:42:44)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:43:17)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:43:50)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:44:23)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:44:55)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:45:35)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:46:07)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:46:40)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:47:22)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:47:54)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:48:28)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:49:01)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:49:34)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:50:06)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:50:39)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:51:11)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:51:44)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:52:16)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:52:50)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:53:22)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:53:54)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:54:27)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:55:00)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:55:33)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:56:05)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:56:37)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:57:09)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:57:42)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:58:14)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:58:47)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
NOROOT
```

### Execution (2026-09-23 15:59:30)
```python
import os; print('ROOTREADY' if os.path.isdir('/content/drive/MyDrive/final aic/audio') else 'NOROOT')

```

**Output**:
```
ROOTREADY
```

### Execution (2026-09-23 15:59:32)
```python
import os
from pathlib import Path
print('mounted', os.path.isdir('/content/drive/MyDrive'))
R = Path('/content/drive/MyDrive/final aic')
print('root', R.exists())
if R.exists():
    for d in ['audio', 'transcripts']:
        print(d, sorted(p.name for p in (R/d).iterdir()) if (R/d).exists() else 'MISSING')
    t = R/'transcripts'/'_write_test.tmp'
    try: t.write_text('x'); t.unlink(); print('write OK')
    except Exception as e: print('write FAIL', e)
else:
    print(sorted(os.listdir('/content/drive/MyDrive'))[:30] if os.path.isdir('/content/drive/MyDrive') else '')

```

**Output**:
```
mounted True
root True
audio ['S01-V001.wav', 'S01-V002.wav', 'S01-V003.wav', 'S01-V004.wav', 'S01-V005.wav', 'S01-V006.wav', 'S01-V007.wav', 'S01-V008.wav', 'S01-V009.wav', 'S01-V010.wav', 'S01-V011.wav', 'S01-V012.wav']
transcripts ['S01-V001.json', 'S01-V002.json', 'S01-V003.json', 'S01-V004.json', 'S01-V005.json', 'S01-V006.json', 'S01-V007.json', 'S01-V008.json']
write OK
```

*File Operation*: `upload` on `/content/mtimes.py`

*File Operation*: `download` on `/content/mt.txt`

*File Operation*: `download` on `/content/mt.txt`

## Session Created: 2026-09-24 01:38:32
- Endpoint: `gpu-t4-s-kkb-ass1c2-3i8p35qp8fx6f`

### Execution (2026-09-24 01:40:04)
```python
import subprocess, sys, glob
sh = lambda c: print(subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip())
sh('nvidia-smi --query-gpu=name,driver_version --format=csv,noheader; nvcc --version | tail -1')
sh(f'{sys.executable} -m pip list 2>/dev/null | grep -iE "^(torch|ctranslate2|faster-whisper|nvidia-cublas|nvidia-cudnn)"')
import torch; print('torch', torch.__version__, 'cuda', torch.version.cuda, 'cudnn', torch.backends.cudnn.version())
print('libcublas:', sorted({p.split('/')[-1] for p in glob.glob('/usr/**/libcublas.so*', recursive=True) + glob.glob(sys.prefix + '/lib/python3*/*-packages/nvidia/**/libcublas*.so*', recursive=True)}))
print('libcudnn:', sorted({p.split('/')[-1] for p in glob.glob(sys.prefix + '/lib/python3*/*-packages/nvidia/**/libcudnn.so*', recursive=True) + glob.glob('/usr/**/libcudnn.so*', recursive=True)}))

```

**Output**:
```
Tesla T4, 580.82.07
Build cuda_13.3.r13.3/compiler.38244171_0
```

**Output**:
```
nvidia-cublas                         13.1.0.3
nvidia-cublas-cu12                    12.9.2.10
nvidia-cudnn-cu12                     9.26.0.51
nvidia-cudnn-cu13                     9.19.0.56
torch                                 2.11.0+cu130
torchao                               0.10.0
torchaudio                            2.11.0+cu130
torchcodec                            0.11.0+cu130
torchdata                             0.11.0
torchsummary                          1.5.1
torchtune                             0.6.1
torchvision                           0.26.0+cu130
```

**Output**:
```
torch 2.11.0+cu130 cuda 13.0 cudnn 92600
```

**Output**:
```
libcublas: ['libcublas.so', 'libcublas.so.12', 'libcublas.so.13', 'libcublas.so.13.6.0.2']
```

**Output**:
```
libcudnn: ['libcudnn.so', 'libcudnn.so.9', 'libcudnn.so.9.24.0']
```

### Execution (2026-09-24 01:43:16)
```python
import os; print('MOUNTED' if os.path.isdir('/content/drive/MyDrive') else 'NOT_MOUNTED')

```

**Output**:
```
NOT_MOUNTED
```

### Execution (2026-09-24 01:43:53)
```python
import os, glob, json
from pathlib import Path
R = Path('/content/drive/MyDrive/AIC')
print('exists', R.exists())
for p in sorted(R.iterdir()):
    n = len(os.listdir(p)) if p.is_dir() else p.stat().st_size
    print(('D ' if p.is_dir() else 'F ') + p.name, n)
for nb in R.glob('voice_2_text*'):
    print('=====', nb)
    if nb.suffix == '.ipynb':
        for i, c in enumerate(json.load(open(nb))['cells']):
            print(f'--- cell {i} [{c["cell_type"]}]'); print(''.join(c['source']))

```

**Output**:
```
exists True
```

**Output**:
```
D Audio 1
F Copy of keyframe.ipynb 186342
D Transcripts 1
F Transcripts_video.zip 3476619
```

**Output**:
```
D data 34
F extract_audio 19837
```

**Output**:
```
D source 31
F test_transcript.ipynb 152012
F voice_2_text 16624
===== /content/drive/MyDrive/AIC/voice_2_text
```

### Execution (2026-09-24 01:44:15)
```python
import os, json
from pathlib import Path
R = Path('/content/drive/MyDrive/AIC')
for d in ['Audio', 'Transcripts']:
    for sub in sorted((R / d).iterdir()):
        fs = os.listdir(sub) if sub.is_dir() else []
        print(d, '/', sub.name, len(fs), sorted(fs)[:3], sorted(fs)[-3:])
raw = open(R / 'voice_2_text', 'rb').read()
print('head', raw[:80])
nb = json.loads(raw)
for i, c in enumerate(nb['cells']):
    print(f'--- cell {i} [{c["cell_type"]}]'); print(''.join(c['source']))

```

**Output**:
```
Audio / video 1177 ['L21_V001.wav', 'L21_V002.wav', 'L21_V003.wav'] ['M10_V029.wav', 'M10_V030.wav', 'M10_V031.wav']
```

**Output**:
```
Transcripts / video 961 ['L21_V001.json', 'L21_V002.json', 'L21_V003.json'] ['M03_V026.json', 'M03_V027.json', 'M03_V028.json']
```

**Output**:
```
head b'{"nbformat":4,"nbformat_minor":0,"metadata":{"colab":{"provenance":[]},"kernelsp'
--- cell 0 [code]
!pip install faster-whisper
--- cell 1 [code]
# !pip install nvidia-cublas-cu12 nvidia-cudnn-cu12

# import os
# import glob

# # Cập nhật lại đường dẫn thư viện đồ họa để Colab nhận diện được CUDA 12
# cublas_path = glob.glob('/usr/local/lib/python*/dist-packages/nvidia/cublas/lib')
# cudnn_path = glob.glob('/usr/local/lib/python*/dist-packages/nvidia/cudnn/lib')

# if cublas_path:
#     os.environ['LD_LIBRARY_PATH'] = cublas_path[0] + ':' + os.environ.get('LD_LIBRARY_PATH', '')
# if cudnn_path:
#     os.environ['LD_LIBRARY_PATH'] = cudnn_path[0] + ':' + os.environ.get('LD_LIBRARY_PATH', '')

# print("Đã vá lỗi thư viện GPU xong!")
--- cell 2 [markdown]
# **VAD chunking -> transcribe từng chunk.**
--- cell 3 [code]
from pathlib import Path
from google.colab import drive
import os
from faster_whisper import WhisperModel
from faster_whisper.audio import decode_audio
from faster_whisper.vad import get_speech_timestamps, VadOptions

drive.mount('/content/drive')


def transcribe_with_faster_whisper(
    audio_path: str | Path,
    *,
    model_id: str = "large-v3",
    device: str = "cuda",
    compute_type: str = "float16",
    language: str = "vi",
) -> list[dict]:
    model = WhisperModel(model_id, device=device, compute_type=compute_type)
    return transcribe_vad_chunks(model, str(audio_path), language)


def transcribe_vad_chunks(model, audio_path: str, language: str) -> list[dict]:
    """VAD trước -> transcribe từng chunk -> timestamp khớp ranh giới BTV."""
    SAMPLE_RATE = 16000
    audio = decode_audio(audio_path, sampling_rate=SAMPLE_RATE)
    vad_options = VadOptions(min_silence_duration_ms=300,
                             speech_pad_ms=50,
                             min_speech_duration_ms=1000,)
    speech_chunks = get_speech_timestamps(audio, vad_options, SAMPLE_RATE)
    if not speech_chunks:
        return []

    result = []
    for chunk in speech_chunks:
        start_sample, end_sample = chunk["start"], chunk["end"]
        start_sec = start_sample / SAMPLE_RATE
        end_sec = end_sample / SAMPLE_RATE
        audio_slice = audio[start_sample:end_sample]

        segments, _ = model.transcribe(
            audio_slice,
            language=language,
            vad_filter=False,
            temperature=0,
            beam_size=5,
            word_timestamps=False,
            condition_on_previous_text=True,
            without_timestamps=False,
            )
        text_parts = [s.text.strip() for s in segments if s.text.strip()]
        text = " ".join(text_parts)
        if text:
            seg = {"start": round(start_sec, 2), "end": round(end_sec, 2), "text": text}
            if not _is_hallucination(seg):
                result.append(seg)
    return result


def _is_hallucination(seg: dict, max_chars_per_sec: float = 80, max_repeat_count: int = 6) -> bool:
    """Lọc hallucination: text lặp hoặc duration ngắn + text dài."""
    duration = seg["end"] - seg["start"]
    text = seg["text"]
    if duration <= 0:
        return True
    chars_per_sec = len(text) / duration
    if chars_per_sec > max_chars_per_sec:
        return True
    words = text.split()
    for n in (2, 3):
        for i in range(len(words) - n + 1):
            phrase = " ".join(words[i : i + n])
            if len(phrase) < 5:
                continue
            if text.count(phrase) >= max_repeat_count:
                return True
    return False


--- cell 4 [code]
import json

def save_transcript_json(segments: list[dict], out_dir: Path, base_name: str):
    """Lưu transcript ra file JSON: [{"start": float, "end": float, "text": str}, ...]"""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{base_name}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(segments, f, ensure_ascii=False, indent=2)
    print(f"  -> {base_name}.json")
--- cell 5 [markdown]
# **Load model 1 lần - xử lý nhiều file**
--- cell 6 [code]
# CẤU HÌNH BATCH
INPUT_DIR_BATCH = Path("/content/drive/MyDrive/AIC/Audio")
OUTPUT_DIR_BATCH = Path("/content/drive/MyDrive/AIC/Transcripts")
OUTPUT_DIR_BATCH.mkdir(parents=True, exist_ok=True)

MODEL_ID_BATCH = "kiendt/PhoWhisper-large-ct2"
DEVICE_BATCH = "cuda"
LANGUAGE_BATCH = "vi"

# LẤY TẤT CẢ DANH SÁCH FILE WAV
all_wav = sorted(list(INPUT_DIR_BATCH.rglob("*.wav")))
print(f"Tìm thấy tổng cộng: {len(all_wav)} file wav.")

# QUÉT NHANH ĐỂ PHÂN LOẠI
to_process = []
skipped_count = 0

for ap in all_wav:
    relative_path = ap.relative_to(INPUT_DIR_BATCH)
    json_out = OUTPUT_DIR_BATCH / relative_path.with_suffix('.json')

    if json_out.exists():
        skipped_count += 1
    else:
        to_process.append((ap, json_out, relative_path))

print(f"--> Bỏ qua {skipped_count} file đã tồn tại ")
print(f"--> Xử lý mới: {len(to_process)} file.")
print("-" * 30)

# LOAD MODEL
if not to_process:
    print("Tất cả các file đều đã được xử lý.")
else:
    print(f"Model: {MODEL_ID_BATCH}...")
    model_batch = WhisperModel(MODEL_ID_BATCH, device=DEVICE_BATCH, compute_type="float16")
    # model_batch = WhisperModel(MODEL_ID_BATCH, device='cpu', compute_type="int8")

    success_count = 0
    for ap, json_out, rel_path in to_process:
        # Tạo thư mục con nếu chưa có
        json_out.parent.mkdir(parents=True, exist_ok=True)

        try:
            segs = transcribe_vad_chunks(model_batch, str(ap), LANGUAGE_BATCH)
            save_transcript_json(segs, json_out.parent, ap.stem)
            success_count += 1

            if success_count % 10 == 0:
                print(f"Đã xử lý {success_count}/{len(to_process)} file. [Vị trí: {rel_path}]")

        except Exception as e:
            print(f"  !! LỖI tại {rel_path}: {e}")

    print(f"Xử lý thành công {success_count} file mới.")
--- cell 7 [code]
# import shutil
# from pathlib import Path
# from google.colab import files

# # =========================================================
# # CẤU HÌNH ĐƯỜNG DẪN NÉN
# # =========================================================
# # 1. Thư mục chứa các file json (Dựa theo ảnh của bạn: Transcripts/video)
# TARGET_FOLDER = Path("/content/drive/MyDrive/AIC/Transcripts/video")

# # Nếu muốn nén TOÀN BỘ thư mục Transcripts (gồm tất cả thư mục con), dùng dòng dưới:
# # TARGET_FOLDER = Path("/content/drive/MyDrive/AIC/Transcripts")

# # 2. Tên file ZIP đầu ra
# ZIP_NAME = "Transcripts_video"  # Tên file không cần đuôi .zip

# # Đường dẫn lưu file zip trên Colab đệm để tải về cho nhanh
# LOCAL_ZIP_PATH = f"/content/{ZIP_NAME}"

# # Đường dẫn lưu dự phòng 1 bản lên Google Drive (tùy chọn)
# DRIVE_ZIP_PATH = f"/content/drive/MyDrive/AIC/{ZIP_NAME}"

# # =========================================================
# # THỰC HIỆN NÉN VÀ TẢI VỀ
# # ==========================================
# if TARGET_FOLDER.exists():
#     print(f" Đang nén thư mục: {TARGET_FOLDER} ...")

#     # Nén trực tiếp và ghi file vào Google Drive
#     output_zip = shutil.make_archive(DRIVE_ZIP_PATH, 'zip', TARGET_FOLDER)

#     print(f"Nén hoàn tất!")
#     print(f"File ZIP đã được lưu tại Google Drive: {output_zip}")
#     print(f"Kích thước: {Path(output_zip).stat().st_size / (1024*1024):.2f} MB")

# else:
#     print(f"❌ Không tìm thấy thư mục: {TARGET_FOLDER}")
```

## Session Created: 2026-09-24 07:47:32
- Endpoint: `m-s-kkb-use1b2-2hfw5omd0nndw`

### Execution (2026-09-24 08:11:49)
```python
# Kiem tra AIC/Transcripts so voi AIC/Audio: du file, JSON hop le, dung schema, thu tu thoi gian.
import json, time
from pathlib import Path
A = Path('/content/drive/MyDrive/AIC/Audio'); T = Path('/content/drive/MyDrive/AIC/Transcripts')
wavs = sorted(A.rglob('*.wav'))
missing, bad, empty, today = [], [], [], 0
since = time.time() - 8 * 3600
for w in wavs:
    j = T / w.relative_to(A).with_suffix('.json')
    if not j.exists():
        missing.append(w.stem); continue
    try:
        d = json.loads(j.read_text(encoding='utf-8'))
        assert isinstance(d, list)
        for s in d:
            assert set(s) == {'start', 'end', 'text'} and s['end'] > s['start'] and s['text'].strip()
        assert all(a['start'] <= b['start'] for a, b in zip(d, d[1:]))
        if not d: empty.append(w.stem)
    except Exception as e:
        bad.append((w.stem, repr(e)[:80]))
    if j.stat().st_mtime > since: today += 1
print(f'WAV {len(wavs)} | JSON thieu {len(missing)} {missing[:20]}')
print(f'JSON loi {len(bad)} {bad[:10]}')
print(f'JSON rong [] {len(empty)} | tao trong 8h qua: {today}')
import os, collections
names = os.listdir(T / 'video')
print('so muc trong Transcripts/video:', len(names), '| ten la (khong phai <stem>.json cua wav):',
      sorted(set(names) - {w.stem + '.json' for w in wavs})[:20])
print('ten trung:', [n for n, c in collections.Counter(names).items() if c > 1][:20])
for s in ['M07_V029', 'M07_V030', 'M07_V031', 'M07_V032', 'M08_V001']:
    p = T / 'video' / f'{s}.json'
    print(s, time.strftime('%H:%M:%S', time.gmtime(p.stat().st_mtime)), p.stat().st_size, len(json.loads(p.read_text(encoding='utf-8'))))

```

**Output**:
```
WAV 1177 | JSON thieu 0 []
JSON loi 0 []
JSON rong [] 30 | tao trong 8h qua: 216
so muc trong Transcripts/video: 1182 | ten la (khong phai <stem>.json cua wav): ['M07_V028 (1).json', 'M07_V029 (1).json', 'M07_V030 (1).json', 'M07_V031 (1).json', 'M07_V032 (1).json']
ten trung: []
M07_V029 07:44:10 38919 165
M07_V030 07:41:24 41158 144
M07_V031 07:38:30 35122 127
M07_V032 07:36:07 42091 168
M08_V001 07:33:12 42921 163
```

### Execution (2026-09-24 08:12:21)
```python
# Xoa ban trung "<stem> (1).json" do may 2 ghi de khi Drive chua dong bo; chi xoa khi noi dung ~ giong ban goc.
import difflib, json
from pathlib import Path
V = Path('/content/drive/MyDrive/AIC/Transcripts/video')
for dup in sorted(V.glob('* (1).json')):
    orig = V / (dup.name.replace(' (1).json', '.json'))
    a = json.loads(orig.read_text(encoding='utf-8')); b = json.loads(dup.read_text(encoding='utf-8'))
    ta = ' '.join(s['text'] for s in a); tb = ' '.join(s['text'] for s in b)
    sim = difflib.SequenceMatcher(None, ta, tb).ratio()
    same_ts = [(s['start'], s['end']) for s in a] == [(s['start'], s['end']) for s in b]
    print(f'{dup.name}: {len(b)} vs goc {len(a)} doan, cung moc thoi gian={same_ts}, do giong text={sim:.3f}', end=' ')
    if same_ts and sim > 0.97:
        dup.unlink(); print('-> DA XOA')
    else:
        print('-> GIU LAI (khac nhieu)')
import os
print('con lai:', len(os.listdir(V)), 'muc; ten la:', [n for n in os.listdir(V) if '(' in n])

```

**Output**:
```
M07_V028 (1).json: 133 vs goc 133 doan, cung moc thoi gian=True, do giong text=1.000 -> DA XOA
```

**Output**:
```
M07_V029 (1).json: 165 vs goc 165 doan, cung moc thoi gian=True, do giong text=1.000 -> DA XOA
```

**Output**:
```
M07_V030 (1).json: 144 vs goc 144 doan, cung moc thoi gian=True, do giong text=1.000 -> DA XOA
```

**Output**:
```
M07_V031 (1).json: 127 vs goc 127 doan, cung moc thoi gian=True, do giong text=1.000 -> DA XOA
```

**Output**:
```
M07_V032 (1).json: 168 vs goc 168 doan, cung moc thoi gian=True, do giong text=1.000 -> DA XOA
con lai: 1177 muc; ten la: []
```

## Session Created: 2026-10-03 05:32:01
- Endpoint: `gpu-t4-s-kkb-use1c2-j9rv3gau4ei8`

## Session Created: 2026-10-03 06:35:42
- Endpoint: `gpu-t4-s-kkb-usw4a2-c1x6zivge9cq`

## Session Created: 2026-10-03 06:35:44
- Endpoint: `m-s-kkb-use1b0-2ugkq4pe2amxt`

## Session Created: 2026-10-03 07:37:57
- Endpoint: `gpu-t4-s-kkb-ass1a2-fd1uj2cz51n0`

## Session Created: 2026-10-03 08:50:32
- Endpoint: `gpu-t4-s-kkb-ass1a0-35ix749oxna72`

## Session Created: 2026-10-03 08:52:56
- Endpoint: `m-s-kkb-use5c0-3q59f2hzbucmt`

## Session Created: 2026-10-05 02:58:39
- Endpoint: `gpu-t4-s-kkb-usw4a1-3ncm368qod1vk`

*File Operation*: `upload` on `/content/lab.tgz`

### Execution (2026-10-05 02:59:26)
```python
import os, subprocess
os.makedirs("/content/lab", exist_ok=True)
subprocess.run(["tar", "-xzf", "/content/lab.tgz", "-C", "/content/lab"], check=True)
print(subprocess.run("ls -la /content/lab /content/lab/code; nvidia-smi --query-gpu=name,memory.total --format=csv; nproc; free -g; df -h /content | tail -1; python -c 'import torch,timm,torchvision;print(torch.__version__,torchvision.__version__,timm.__version__)'", shell=True, capture_output=True, text=True).stdout)

```

**Output**:
```
/content/lab:
total 40
drwxr-xr-x 3 root   root    4096 Oct  5 02:59 .
drwxr-xr-x 1 root   root    4096 Oct  5 02:59 ..
drwxr-xr-x 2 197609 197121  4096 Oct  5 02:58 code
-rwxr-xr-x 1 197609 197121 25704 Oct  5 02:43 eval.py

/content/lab/code:
total 104
drwxr-xr-x 2 197609 197121  4096 Oct  5 02:58 .
drwxr-xr-x 3 root   root    4096 Oct  5 02:59 ..
-rw-r--r-- 1 197609 197121  2984 Oct  5 02:56 benchmark.py
-rw-r--r-- 1 197609 197121  9981 Oct  5 02:53 dataset.py
-rw-r--r-- 1 197609 197121  3418 Oct  5 02:58 experiments.py
-rw-r--r-- 1 197609 197121  7256 Oct  5 02:56 inference.py
-rw-r--r-- 1 197609 197121 10175 Oct  5 02:53 lab_day2.ipynb
-rw-r--r-- 1 197609 197121  4922 Oct  5 02:55 losses.py
-rw-r--r-- 1 197609 197121  4877 Oct  5 02:54 model.py
-rw-r--r-- 1 197609 197121  7468 Oct  5 02:58 step0_prepare.py
-rw-r--r-- 1 197609 197121  7407 Oct  5 02:57 test_code.py
-rw-r--r-- 1 197609 197121 20911 Oct  5 02:55 train.py
name, memory.total [MiB]
Tesla T4, 15360 MiB
2
               total        used        free      shared  buff/cache   available
Mem:              12           0           8           0           3          11
Swap:              0           0           0
overlay         113G   43G   71G  38% /
2.11.0+cu130 0.26.0+cu130 1.0.29

```

### Execution (2026-10-05 02:59:40)
```python
import os
os.environ['CMD'] = 'mkdir -p logs; python -u code/step0_prepare.py'
os.environ['LOG'] = 'logs/step0.log'
# Chạy lệnh nền trên VM: biến môi trường CMD và LOG
import os, subprocess
cmd, log = os.environ["CMD"], os.environ["LOG"]
subprocess.Popen(f"cd /content/lab && nohup {cmd} > {log} 2>&1 &", shell=True)
print("launched:", cmd, "->", log)

```

**Output**:
```
launched: mkdir -p logs; python -u code/step0_prepare.py -> logs/step0.log
```

### Execution (2026-10-05 02:59:51)
```python
import os
os.environ['SH'] = 'tail -n 40 logs/step0.log; ls -la data'
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
Tải images.zip ...
total 134024
drwxr-xr-x 3 root root      4096 Oct  5 02:59 .
drwxr-xr-x 6 root root      4096 Oct  5 02:59 ..
-rw-r--r-- 1 root root 137225660 Oct  5 02:59 images.zip
drwxr-xr-x 2 root root      4096 Oct  5 02:59 labels

```

### Execution (2026-10-05 03:00:00)
```python
import os
os.environ['SH'] = 'tail -n 60 logs/step0.log'
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
Tải images.zip ...

```

### Execution (2026-10-05 03:00:34)
```python
import os
os.environ['SH'] = 'tail -n 60 logs/step0.log'
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
Tải images.zip ...
MD5 OK: b7b30f96d466fba86016aa5a26606e0f
Số file ảnh: 17509
Số ảnh: {'train': 10501, 'val': 3501, 'test': 3507} | tỉ lệ: {'train': 0.5997, 'val': 0.2, 'test': 0.2003}
                train   val  test  total
Chinee Apple      675   225   226   1126
Lantana           637   213   213   1063
Parkinsonia       618   206   207   1031
Parthenium        613   204   205   1022
Prickly Acacia    637   212   213   1062
Rubber Vine       605   202   202   1009
Siam Weed         644   215   215   1074
Snake Weed        609   203   204   1016
Negatives        5463  1821  1822   9106
Giao: {'train&val': 0, 'train&test': 0, 'val&test': 0} | hợp: 17509 | file thiếu: 0
                train   val  test  total  paper_table1  diff_vs_paper
Chinee Apple      675   225   226   1126          1125              1
Lantana           637   213   213   1063          1064             -1
Parkinsonia       618   206   207   1031          1031              0
Parthenium        613   204   205   1022          1022              0
Prickly Acacia    637   212   213   1062          1062              0
Rubber Vine       605   202   202   1009          1009              0
Siam Weed         644   215   215   1074          1074              0
Snake Weed        609   203   204   1016          1016              0
Negatives        5463  1821  1822   9106          9106              0
Giải mã 17509 ảnh vào cache data/images_uint8_17509.npy (chỉ chạy một lần)...

```

### Execution (2026-10-05 03:01:07)
```python
import os
os.environ['SH'] = 'tail -n 60 logs/step0.log'
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
Tải images.zip ...
MD5 OK: b7b30f96d466fba86016aa5a26606e0f
Số file ảnh: 17509
Số ảnh: {'train': 10501, 'val': 3501, 'test': 3507} | tỉ lệ: {'train': 0.5997, 'val': 0.2, 'test': 0.2003}
                train   val  test  total
Chinee Apple      675   225   226   1126
Lantana           637   213   213   1063
Parkinsonia       618   206   207   1031
Parthenium        613   204   205   1022
Prickly Acacia    637   212   213   1062
Rubber Vine       605   202   202   1009
Siam Weed         644   215   215   1074
Snake Weed        609   203   204   1016
Negatives        5463  1821  1822   9106
Giao: {'train&val': 0, 'train&test': 0, 'val&test': 0} | hợp: 17509 | file thiếu: 0
                train   val  test  total  paper_table1  diff_vs_paper
Chinee Apple      675   225   226   1126          1125              1
Lantana           637   213   213   1063          1064             -1
Parkinsonia       618   206   207   1031          1031              0
Parthenium        613   204   205   1022          1022              0
Prickly Acacia    637   212   213   1062          1062              0
Rubber Vine       605   202   202   1009          1009              0
Siam Weed         644   215   215   1074          1074              0
Snake Weed        609   203   204   1016          1016              0
Negatives        5463  1821  1822   9106          9106              0
Giải mã 17509 ảnh vào cache data/images_uint8_17509.npy (chỉ chạy một lần)...

```

### Execution (2026-10-05 03:01:38)
```python
import os
os.environ['SH'] = 'tail -n 40 logs/step0.log; ls -la data; ls data/images | wc -l; free -g | head -2'
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
Tải images.zip ...
MD5 OK: b7b30f96d466fba86016aa5a26606e0f
Số file ảnh: 17509
Số ảnh: {'train': 10501, 'val': 3501, 'test': 3507} | tỉ lệ: {'train': 0.5997, 'val': 0.2, 'test': 0.2003}
                train   val  test  total
Chinee Apple      675   225   226   1126
Lantana           637   213   213   1063
Parkinsonia       618   206   207   1031
Parthenium        613   204   205   1022
Prickly Acacia    637   212   213   1062
Rubber Vine       605   202   202   1009
Siam Weed         644   215   215   1074
Snake Weed        609   203   204   1016
Negatives        5463  1821  1822   9106
Giao: {'train&val': 0, 'train&test': 0, 'val&test': 0} | hợp: 17509 | file thiếu: 0
                train   val  test  total  paper_table1  diff_vs_paper
Chinee Apple      675   225   226   1126          1125              1
Lantana           637   213   213   1063          1064             -1
Parkinsonia       618   206   207   1031          1031              0
Parthenium        613   204   205   1022          1022              0
Prickly Acacia    637   212   213   1062          1062              0
Rubber Vine       605   202   202   1009          1009              0
Siam Weed         644   215   215   1074          1074              0
Snake Weed        609   203   204   1016          1016              0
Negatives        5463  1821  1822   9106          9106              0
Giải mã 17509 ảnh vào cache data/images_uint8_17509.npy (chỉ chạy một lần)...
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Loss ban đầu: 2.1803 (ln 9 = 2.1972)
Overfit 16 ảnh: loss 2.2180 -> 0.000149
BƯỚC 0 XONG
total 3842584
drwxr-xr-x 4 root root       4096 Oct  5 03:01 .
drwxr-xr-x 7 root root       4096 Oct  5 03:01 ..
drwxr-xr-x 2 root root     851968 Oct  5 03:00 images
-rw-r--r-- 1 root root 3442409600 Oct  5 03:01 images_uint8_17509.npy
-rw-r--r-- 1 root root  491516047 Oct  5 03:00 images.zip
drwxr-xr-x 2 root root       4096 Oct  5 03:00 labels
17509
               total        used        free      shared  buff/cache   available
Mem:              12           6           0           0           7           6

```

### Execution (2026-10-05 03:01:41)
```python
import os
os.environ['SH'] = 'tail -n 60 logs/step0.log'
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
Tải images.zip ...
MD5 OK: b7b30f96d466fba86016aa5a26606e0f
Số file ảnh: 17509
Số ảnh: {'train': 10501, 'val': 3501, 'test': 3507} | tỉ lệ: {'train': 0.5997, 'val': 0.2, 'test': 0.2003}
                train   val  test  total
Chinee Apple      675   225   226   1126
Lantana           637   213   213   1063
Parkinsonia       618   206   207   1031
Parthenium        613   204   205   1022
Prickly Acacia    637   212   213   1062
Rubber Vine       605   202   202   1009
Siam Weed         644   215   215   1074
Snake Weed        609   203   204   1016
Negatives        5463  1821  1822   9106
Giao: {'train&val': 0, 'train&test': 0, 'val&test': 0} | hợp: 17509 | file thiếu: 0
                train   val  test  total  paper_table1  diff_vs_paper
Chinee Apple      675   225   226   1126          1125              1
Lantana           637   213   213   1063          1064             -1
Parkinsonia       618   206   207   1031          1031              0
Parthenium        613   204   205   1022          1022              0
Prickly Acacia    637   212   213   1062          1062              0
Rubber Vine       605   202   202   1009          1009              0
Siam Weed         644   215   215   1074          1074              0
Snake Weed        609   203   204   1016          1016              0
Negatives        5463  1821  1822   9106          9106              0
Giải mã 17509 ảnh vào cache data/images_uint8_17509.npy (chỉ chạy một lần)...
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Loss ban đầu: 2.1803 (ln 9 = 2.1972)
Overfit 16 ảnh: loss 2.2180 -> 0.000149
BƯỚC 0 XONG

```

*File Operation*: `upload` on `/content/lab/code/step3_inference.py`

### Execution (2026-10-05 03:01:54)
```python
import os
os.environ['CMD'] = 'python -u code/experiments.py B01'
os.environ['LOG'] = 'logs/B01.log'
# Chạy lệnh nền trên VM: biến môi trường CMD và LOG
import os, subprocess
cmd, log = os.environ["CMD"], os.environ["LOG"]
subprocess.Popen(f"cd /content/lab && nohup {cmd} > {log} 2>&1 &", shell=True)
print("launched:", cmd, "->", log)

```

**Output**:
```
launched: python -u code/experiments.py B01 -> logs/B01.log
```

### Execution (2026-10-05 03:02:03)
```python
import os
os.environ['SH'] = 'tail -n 25 logs/B01.log'
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.

```

### Execution (2026-10-05 03:02:10)
```python
import os
os.environ['SH'] = 'tail -n 15 logs/B01.log; nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv; top -bn1 | head -12'
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
utilization.gpu [%], memory.used [MiB]
97 %, 3737 MiB
top - 03:02:11 up 15 min,  0 user,  load average: 1.93, 0.93, 0.41
Tasks:  19 total,   3 running,  15 sleeping,   0 stopped,   1 zombie
%Cpu(s): 73.9 us, 21.7 sy,  0.0 ni,  0.0 id,  4.3 wa,  0.0 hi,  0.0 si,  0.0 st 
MiB Mem :  12975.5 total,   1670.4 free,   2974.5 used,   9021.7 buff/cache     
MiB Swap:      0.0 total,      0.0 free,      0.0 used.  10001.1 avail Mem 

    PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
   3673 root      20   0   18.7g   2.2g 976556 S  90.0  17.3   0:13.52 python3
   3705 root      20   0   11.8g 928028 390752 R  50.0   7.0   0:02.68 pt_data+
   3706 root      20   0   11.8g 915960 378684 R  30.0   6.9   0:02.58 pt_data+
      1 root      20   0     988    564    508 S   0.0   0.0   0:00.03 docker-+
      8 root      20   0 1161100  57492  41444 S   0.0   0.4   0:00.65 node

```

### Execution (2026-10-05 03:02:37)
```python
import os
os.environ['SH'] = 'tail -n 25 logs/B01.log'
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.

```

### Execution (2026-10-05 03:03:20)
```python
import os
os.environ['SH'] = 'tail -n 25 logs/B01.log'
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
[B01 s0] ep  1 train_loss 1.6549 val_loss 1.2657 F1 0.1942 top1 0.5547 (35s)

```

### Execution (2026-10-05 03:03:35)
```python
import os
os.environ['SH'] = "grep -E 'ep ' logs/B01.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
[B01 s0] ep  1 train_loss 1.6549 val_loss 1.2657 F1 0.1942 top1 0.5547 (35s)
[B01 s0] ep  2 train_loss 0.9751 val_loss 0.7954 F1 0.5802 top1 0.7149 (32s)

```

### Execution (2026-10-05 03:03:54)
```python
import os
os.environ['SH'] = 'tail -n 25 logs/B01.log'
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
[B01 s0] ep  1 train_loss 1.6549 val_loss 1.2657 F1 0.1942 top1 0.5547 (35s)
[B01 s0] ep  2 train_loss 0.9751 val_loss 0.7954 F1 0.5802 top1 0.7149 (32s)

```

### Execution (2026-10-05 03:04:27)
```python
import os
os.environ['SH'] = 'tail -n 25 logs/B01.log'
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
[B01 s0] ep  1 train_loss 1.6549 val_loss 1.2657 F1 0.1942 top1 0.5547 (35s)
[B01 s0] ep  2 train_loss 0.9751 val_loss 0.7954 F1 0.5802 top1 0.7149 (32s)
[B01 s0] ep  3 train_loss 0.6976 val_loss 0.6108 F1 0.6988 top1 0.7889 (32s)

```

### Execution (2026-10-05 03:05:01)
```python
import os
os.environ['SH'] = 'tail -n 25 logs/B01.log'
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
[B01 s0] ep  1 train_loss 1.6549 val_loss 1.2657 F1 0.1942 top1 0.5547 (35s)
[B01 s0] ep  2 train_loss 0.9751 val_loss 0.7954 F1 0.5802 top1 0.7149 (32s)
[B01 s0] ep  3 train_loss 0.6976 val_loss 0.6108 F1 0.6988 top1 0.7889 (32s)
[B01 s0] ep  4 train_loss 0.5830 val_loss 0.5489 F1 0.7436 top1 0.8118 (33s)

```

### Execution (2026-10-05 03:05:38)
```python
import os
os.environ['SH'] = 'tail -n 25 logs/B01.log'
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
[B01 s0] ep  1 train_loss 1.6549 val_loss 1.2657 F1 0.1942 top1 0.5547 (35s)
[B01 s0] ep  2 train_loss 0.9751 val_loss 0.7954 F1 0.5802 top1 0.7149 (32s)
[B01 s0] ep  3 train_loss 0.6976 val_loss 0.6108 F1 0.6988 top1 0.7889 (32s)
[B01 s0] ep  4 train_loss 0.5830 val_loss 0.5489 F1 0.7436 top1 0.8118 (33s)
[B01 s0] ep  5 train_loss 0.5101 val_loss 0.5238 F1 0.7566 top1 0.8243 (34s)

```

### Execution (2026-10-05 03:06:11)
```python
import os
os.environ['SH'] = 'tail -n 25 logs/B01.log'
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
[B01 s0] ep  1 train_loss 1.6549 val_loss 1.2657 F1 0.1942 top1 0.5547 (35s)
[B01 s0] ep  2 train_loss 0.9751 val_loss 0.7954 F1 0.5802 top1 0.7149 (32s)
[B01 s0] ep  3 train_loss 0.6976 val_loss 0.6108 F1 0.6988 top1 0.7889 (32s)
[B01 s0] ep  4 train_loss 0.5830 val_loss 0.5489 F1 0.7436 top1 0.8118 (33s)
[B01 s0] ep  5 train_loss 0.5101 val_loss 0.5238 F1 0.7566 top1 0.8243 (34s)
[B01 s0] ep  6 train_loss 0.4768 val_loss 0.4910 F1 0.7722 top1 0.8349 (34s)

```

### Execution (2026-10-05 03:06:38)
```python
import os
os.environ['SH'] = "grep -E 'ep |QUEUE|Error' logs/B01.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
[B01 s0] ep  1 train_loss 1.6549 val_loss 1.2657 F1 0.1942 top1 0.5547 (35s)
[B01 s0] ep  2 train_loss 0.9751 val_loss 0.7954 F1 0.5802 top1 0.7149 (32s)
[B01 s0] ep  3 train_loss 0.6976 val_loss 0.6108 F1 0.6988 top1 0.7889 (32s)
[B01 s0] ep  4 train_loss 0.5830 val_loss 0.5489 F1 0.7436 top1 0.8118 (33s)
[B01 s0] ep  5 train_loss 0.5101 val_loss 0.5238 F1 0.7566 top1 0.8243 (34s)
[B01 s0] ep  6 train_loss 0.4768 val_loss 0.4910 F1 0.7722 top1 0.8349 (34s)

```

### Execution (2026-10-05 03:06:44)
```python
import os
os.environ['SH'] = 'tail -n 25 logs/B01.log'
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
[B01 s0] ep  1 train_loss 1.6549 val_loss 1.2657 F1 0.1942 top1 0.5547 (35s)
[B01 s0] ep  2 train_loss 0.9751 val_loss 0.7954 F1 0.5802 top1 0.7149 (32s)
[B01 s0] ep  3 train_loss 0.6976 val_loss 0.6108 F1 0.6988 top1 0.7889 (32s)
[B01 s0] ep  4 train_loss 0.5830 val_loss 0.5489 F1 0.7436 top1 0.8118 (33s)
[B01 s0] ep  5 train_loss 0.5101 val_loss 0.5238 F1 0.7566 top1 0.8243 (34s)
[B01 s0] ep  6 train_loss 0.4768 val_loss 0.4910 F1 0.7722 top1 0.8349 (34s)

```

### Execution (2026-10-05 03:07:37)
```python
import os
os.environ['SH'] = 'tail -n 25 logs/B01.log'
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
[B01 s0] ep  1 train_loss 1.6549 val_loss 1.2657 F1 0.1942 top1 0.5547 (35s)
[B01 s0] ep  2 train_loss 0.9751 val_loss 0.7954 F1 0.5802 top1 0.7149 (32s)
[B01 s0] ep  3 train_loss 0.6976 val_loss 0.6108 F1 0.6988 top1 0.7889 (32s)
[B01 s0] ep  4 train_loss 0.5830 val_loss 0.5489 F1 0.7436 top1 0.8118 (33s)
[B01 s0] ep  5 train_loss 0.5101 val_loss 0.5238 F1 0.7566 top1 0.8243 (34s)
[B01 s0] ep  6 train_loss 0.4768 val_loss 0.4910 F1 0.7722 top1 0.8349 (34s)
[B01 s0] ep  7 train_loss 0.4411 val_loss 0.4760 F1 0.7774 top1 0.8400 (34s)
[B01 s0] ep  8 train_loss 0.4230 val_loss 0.4753 F1 0.7749 top1 0.8386 (34s)

```

### Execution (2026-10-05 03:08:11)
```python
import os
os.environ['SH'] = 'tail -n 25 logs/B01.log'
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
[B01 s0] ep  1 train_loss 1.6549 val_loss 1.2657 F1 0.1942 top1 0.5547 (35s)
[B01 s0] ep  2 train_loss 0.9751 val_loss 0.7954 F1 0.5802 top1 0.7149 (32s)
[B01 s0] ep  3 train_loss 0.6976 val_loss 0.6108 F1 0.6988 top1 0.7889 (32s)
[B01 s0] ep  4 train_loss 0.5830 val_loss 0.5489 F1 0.7436 top1 0.8118 (33s)
[B01 s0] ep  5 train_loss 0.5101 val_loss 0.5238 F1 0.7566 top1 0.8243 (34s)
[B01 s0] ep  6 train_loss 0.4768 val_loss 0.4910 F1 0.7722 top1 0.8349 (34s)
[B01 s0] ep  7 train_loss 0.4411 val_loss 0.4760 F1 0.7774 top1 0.8400 (34s)
[B01 s0] ep  8 train_loss 0.4230 val_loss 0.4753 F1 0.7749 top1 0.8386 (34s)

```

### Execution (2026-10-05 03:08:45)
```python
import os
os.environ['SH'] = 'tail -n 25 logs/B01.log'
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
[B01 s0] ep  1 train_loss 1.6549 val_loss 1.2657 F1 0.1942 top1 0.5547 (35s)
[B01 s0] ep  2 train_loss 0.9751 val_loss 0.7954 F1 0.5802 top1 0.7149 (32s)
[B01 s0] ep  3 train_loss 0.6976 val_loss 0.6108 F1 0.6988 top1 0.7889 (32s)
[B01 s0] ep  4 train_loss 0.5830 val_loss 0.5489 F1 0.7436 top1 0.8118 (33s)
[B01 s0] ep  5 train_loss 0.5101 val_loss 0.5238 F1 0.7566 top1 0.8243 (34s)
[B01 s0] ep  6 train_loss 0.4768 val_loss 0.4910 F1 0.7722 top1 0.8349 (34s)
[B01 s0] ep  7 train_loss 0.4411 val_loss 0.4760 F1 0.7774 top1 0.8400 (34s)
[B01 s0] ep  8 train_loss 0.4230 val_loss 0.4753 F1 0.7749 top1 0.8386 (34s)
[B01 s0] ep  9 train_loss 0.4184 val_loss 0.4750 F1 0.7754 top1 0.8395 (34s)

```

### Execution (2026-10-05 03:09:06)
```python
import os
os.environ['SH'] = "grep -E 'ep |QUEUE|Error' logs/B01.log; head -c 700 runs/B01/seed0/summary.json"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
[B01 s0] ep  1 train_loss 1.6549 val_loss 1.2657 F1 0.1942 top1 0.5547 (35s)
[B01 s0] ep  2 train_loss 0.9751 val_loss 0.7954 F1 0.5802 top1 0.7149 (32s)
[B01 s0] ep  3 train_loss 0.6976 val_loss 0.6108 F1 0.6988 top1 0.7889 (32s)
[B01 s0] ep  4 train_loss 0.5830 val_loss 0.5489 F1 0.7436 top1 0.8118 (33s)
[B01 s0] ep  5 train_loss 0.5101 val_loss 0.5238 F1 0.7566 top1 0.8243 (34s)
[B01 s0] ep  6 train_loss 0.4768 val_loss 0.4910 F1 0.7722 top1 0.8349 (34s)
[B01 s0] ep  7 train_loss 0.4411 val_loss 0.4760 F1 0.7774 top1 0.8400 (34s)
[B01 s0] ep  8 train_loss 0.4230 val_loss 0.4753 F1 0.7749 top1 0.8386 (34s)
[B01 s0] ep  9 train_loss 0.4184 val_loss 0.4750 F1 0.7754 top1 0.8395 (34s)

```

### Execution (2026-10-05 03:09:18)
```python
import os
os.environ['SH'] = 'tail -n 25 logs/B01.log'
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
[B01 s0] ep  1 train_loss 1.6549 val_loss 1.2657 F1 0.1942 top1 0.5547 (35s)
[B01 s0] ep  2 train_loss 0.9751 val_loss 0.7954 F1 0.5802 top1 0.7149 (32s)
[B01 s0] ep  3 train_loss 0.6976 val_loss 0.6108 F1 0.6988 top1 0.7889 (32s)
[B01 s0] ep  4 train_loss 0.5830 val_loss 0.5489 F1 0.7436 top1 0.8118 (33s)
[B01 s0] ep  5 train_loss 0.5101 val_loss 0.5238 F1 0.7566 top1 0.8243 (34s)
[B01 s0] ep  6 train_loss 0.4768 val_loss 0.4910 F1 0.7722 top1 0.8349 (34s)
[B01 s0] ep  7 train_loss 0.4411 val_loss 0.4760 F1 0.7774 top1 0.8400 (34s)
[B01 s0] ep  8 train_loss 0.4230 val_loss 0.4753 F1 0.7749 top1 0.8386 (34s)
[B01 s0] ep  9 train_loss 0.4184 val_loss 0.4750 F1 0.7754 top1 0.8395 (34s)
[B01 s0] ep 10 train_loss 0.4096 val_loss 0.4662 F1 0.7841 top1 0.8429 (34s)
QUEUE {"exp_id": "B01", "status": "ok", "val_macro_f1": 0.7840761483385995, "min": 7.268623876571655}
QUEUE DONE

```

### Execution (2026-10-05 03:10:11)
```python
import json, subprocess, torch, timm
print(subprocess.run("grep -E 'ep 10|QUEUE' /content/lab/logs/B01.log", shell=True, capture_output=True, text=True).stdout)
s = json.load(open("/content/lab/runs/B01/seed0/summary.json"))
print({k: s[k] for k in ("weight_tag", "params_M", "gmacs", "best_epoch", "val_macro_f1", "val_top1", "train_s_per_epoch")})
print("pretrained resnet50 tags:", timm.list_pretrained("resnet50.*")[:12])
m = timm.create_model("resnet50", pretrained=True, num_classes=9)
r = timm.create_model("resnet50", pretrained=False, num_classes=9)
print("cfg:", m.pretrained_cfg.get("hf_hub_id"), m.pretrained_cfg.get("tag"), m.pretrained_cfg.get("mean"), m.pretrained_cfg.get("crop_pct"))
print("conv1 std pretrained vs random:", m.conv1.weight.std().item(), r.conv1.weight.std().item())
print("bn1 running_var mean pretrained vs random:", m.bn1.running_var.mean().item(), r.bn1.running_var.mean().item())

```

**Output**:
```
[B01 s0] ep 10 train_loss 0.4096 val_loss 0.4662 F1 0.7841 top1 0.8429 (34s)
QUEUE {"exp_id": "B01", "status": "ok", "val_macro_f1": 0.7840761483385995, "min": 7.268623876571655}
QUEUE DONE

{'weight_tag': 'resnet50.a1_in1k', 'params_M': 23.526473, 'gmacs': 4.087154688, 'best_epoch': 10, 'val_macro_f1': 0.7840761483385995, 'val_top1': 0.8429020279920023, 'train_s_per_epoch': 33.653871243200015}
pretrained resnet50 tags: ['resnet50.a1_in1k', 'resnet50.a1h_in1k', 'resnet50.a2_in1k', 'resnet50.a3_in1k', 'resnet50.am_in1k', 'resnet50.b1k_in1k', 'resnet50.b2k_in1k', 'resnet50.bt_in1k', 'resnet50.c1_in1k', 'resnet50.c2_in1k', 'resnet50.d_in1k', 'resnet50.fb_ssl_yfcc100m_ft_in1k']
```

**Output**:
```
/usr/local/lib/python3.13/dist-packages/huggingface_hub/utils/_auth.py:138: UserWarning: 
Error while fetching `HF_TOKEN` secret value from your vault: 'Requesting secret HF_TOKEN timed out. Secrets can only be fetched when running from the Colab UI.'.
  warnings.warn(f"\nError while fetching `HF_TOKEN` secret value from your vault: '{str(e)}'.")
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
```

**Output**:
```
WARNING:huggingface_hub.utils._http:Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
```

**Output**:
```
cfg: timm/resnet50.a1_in1k a1_in1k (0.485, 0.456, 0.406) 0.95
conv1 std pretrained vs random: 0.2487141340970993 0.025437215343117714
bn1 running_var mean pretrained vs random: 35.42747497558594 1.0
```

### Execution (2026-10-05 03:10:28)
```python
# Gói các file nhỏ (không checkpoint, không ảnh) để tải về máy
import subprocess
cmd = ("cd /content/lab && tar -czf /content/artifacts.tgz --exclude='*.pt' "
       "eda curves predictions logs results runs/*/seed*/summary.json runs/*/seed*/history.csv "
       "runs/*/seed*/config.json runs/*/seed*/*.npy runs/queue_log.jsonl 2>/dev/null; ls -la /content/artifacts.tgz")
print(subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout)

```

**Output**:
```
-rw-r--r-- 1 root root 3825056 Oct  5 03:10 /content/artifacts.tgz

```

*File Operation*: `download` on `/content/artifacts.tgz`

### Execution (2026-10-05 03:18:39)
```python
import os
os.environ['CMD'] = 'python -u code/experiments.py B02 B03 B04 B05 B06'
os.environ['LOG'] = 'logs/B02-B06.log'
# Chạy lệnh nền trên VM: biến môi trường CMD và LOG
import os, subprocess
cmd, log = os.environ["CMD"], os.environ["LOG"]
subprocess.Popen(f"cd /content/lab && nohup {cmd} > {log} 2>&1 &", shell=True)
print("launched:", cmd, "->", log)

```

**Output**:
```
launched: python -u code/experiments.py B02 B03 B04 B05 B06 -> logs/B02-B06.log
```

### Execution (2026-10-05 03:18:47)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```

```

*File Operation*: `upload` on `/content/lab/code/step1_latency.py`

### Execution (2026-10-05 03:19:05)
```python
import os
os.environ['SH'] = "grep -E 'ep |QUEUE|Error' logs/B02-B06.log | tail -n 6"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```

```

### Execution (2026-10-05 03:19:50)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```

```

### Execution (2026-10-05 03:20:19)
```python
import os
os.environ['SH'] = 'tail -n 8 logs/B02-B06.log'
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
/content/lab/code/train.py:196: UserWarning: Detected call of `lr_scheduler.step()` before `optimizer.step()`. In PyTorch 1.1.0 and later, you should call them in the opposite order: `optimizer.step()` before `lr_scheduler.step()`.  Failure to do this will result in PyTorch skipping the first value of the learning rate schedule. See more details at https://pytorch.org/docs/stable/optim.html#how-to-adjust-learning-rate
  scheduler.step()
[B02 s0] ep  1 train_loss 0.7622 val_loss 0.3225 F1 0.8573 top1 0.8946 (59s)

```

### Execution (2026-10-05 03:20:54)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```

```

### Execution (2026-10-05 03:21:56)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```

```

### Execution (2026-10-05 03:22:59)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```

```

### Execution (2026-10-05 03:24:03)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```

```

### Execution (2026-10-05 03:25:06)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```

```

### Execution (2026-10-05 03:26:09)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```

```

### Execution (2026-10-05 03:27:13)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```

```

### Execution (2026-10-05 03:28:17)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```

```

### Execution (2026-10-05 03:29:28)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
[B02 s0] ep 10 train_loss 0.0433 val_loss 0.0953 F1 0.9661 top1 0.9749 (49s)
QUEUE {"exp_id": "B02", "status": "ok", "val_macro_f1": 0.9675884081376529, "min": 10.642984124024709}

```

### Execution (2026-10-05 03:30:33)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
[B02 s0] ep 10 train_loss 0.0433 val_loss 0.0953 F1 0.9661 top1 0.9749 (49s)
QUEUE {"exp_id": "B02", "status": "ok", "val_macro_f1": 0.9675884081376529, "min": 10.642984124024709}

```

### Execution (2026-10-05 03:31:37)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
[B02 s0] ep 10 train_loss 0.0433 val_loss 0.0953 F1 0.9661 top1 0.9749 (49s)
QUEUE {"exp_id": "B02", "status": "ok", "val_macro_f1": 0.9675884081376529, "min": 10.642984124024709}

```

### Execution (2026-10-05 03:32:41)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
[B02 s0] ep 10 train_loss 0.0433 val_loss 0.0953 F1 0.9661 top1 0.9749 (49s)
QUEUE {"exp_id": "B02", "status": "ok", "val_macro_f1": 0.9675884081376529, "min": 10.642984124024709}

```

### Execution (2026-10-05 03:33:44)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
[B02 s0] ep 10 train_loss 0.0433 val_loss 0.0953 F1 0.9661 top1 0.9749 (49s)
QUEUE {"exp_id": "B02", "status": "ok", "val_macro_f1": 0.9675884081376529, "min": 10.642984124024709}

```

### Execution (2026-10-05 03:34:51)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
[B02 s0] ep 10 train_loss 0.0433 val_loss 0.0953 F1 0.9661 top1 0.9749 (49s)
QUEUE {"exp_id": "B02", "status": "ok", "val_macro_f1": 0.9675884081376529, "min": 10.642984124024709}

```

### Execution (2026-10-05 03:35:54)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
[B02 s0] ep 10 train_loss 0.0433 val_loss 0.0953 F1 0.9661 top1 0.9749 (49s)
QUEUE {"exp_id": "B02", "status": "ok", "val_macro_f1": 0.9675884081376529, "min": 10.642984124024709}

```

### Execution (2026-10-05 03:36:57)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
[B02 s0] ep 10 train_loss 0.0433 val_loss 0.0953 F1 0.9661 top1 0.9749 (49s)
QUEUE {"exp_id": "B02", "status": "ok", "val_macro_f1": 0.9675884081376529, "min": 10.642984124024709}
[B03 s0] ep 10 train_loss 0.0601 val_loss 0.1267 F1 0.9503 top1 0.9654 (33s)
QUEUE {"exp_id": "B03", "status": "ok", "val_macro_f1": 0.9502624553264576, "min": 6.7240373929341635}

```

### Execution (2026-10-05 03:38:00)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
[B02 s0] ep 10 train_loss 0.0433 val_loss 0.0953 F1 0.9661 top1 0.9749 (49s)
QUEUE {"exp_id": "B02", "status": "ok", "val_macro_f1": 0.9675884081376529, "min": 10.642984124024709}
[B03 s0] ep 10 train_loss 0.0601 val_loss 0.1267 F1 0.9503 top1 0.9654 (33s)
QUEUE {"exp_id": "B03", "status": "ok", "val_macro_f1": 0.9502624553264576, "min": 6.7240373929341635}

```

### Execution (2026-10-05 03:39:04)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
[B02 s0] ep 10 train_loss 0.0433 val_loss 0.0953 F1 0.9661 top1 0.9749 (49s)
QUEUE {"exp_id": "B02", "status": "ok", "val_macro_f1": 0.9675884081376529, "min": 10.642984124024709}
[B03 s0] ep 10 train_loss 0.0601 val_loss 0.1267 F1 0.9503 top1 0.9654 (33s)
QUEUE {"exp_id": "B03", "status": "ok", "val_macro_f1": 0.9502624553264576, "min": 6.7240373929341635}

```

### Execution (2026-10-05 03:40:07)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
[B02 s0] ep 10 train_loss 0.0433 val_loss 0.0953 F1 0.9661 top1 0.9749 (49s)
QUEUE {"exp_id": "B02", "status": "ok", "val_macro_f1": 0.9675884081376529, "min": 10.642984124024709}
[B03 s0] ep 10 train_loss 0.0601 val_loss 0.1267 F1 0.9503 top1 0.9654 (33s)
QUEUE {"exp_id": "B03", "status": "ok", "val_macro_f1": 0.9502624553264576, "min": 6.7240373929341635}

```

### Execution (2026-10-05 03:41:10)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
[B02 s0] ep 10 train_loss 0.0433 val_loss 0.0953 F1 0.9661 top1 0.9749 (49s)
QUEUE {"exp_id": "B02", "status": "ok", "val_macro_f1": 0.9675884081376529, "min": 10.642984124024709}
[B03 s0] ep 10 train_loss 0.0601 val_loss 0.1267 F1 0.9503 top1 0.9654 (33s)
QUEUE {"exp_id": "B03", "status": "ok", "val_macro_f1": 0.9502624553264576, "min": 6.7240373929341635}

```

### Execution (2026-10-05 03:42:14)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
[B02 s0] ep 10 train_loss 0.0433 val_loss 0.0953 F1 0.9661 top1 0.9749 (49s)
QUEUE {"exp_id": "B02", "status": "ok", "val_macro_f1": 0.9675884081376529, "min": 10.642984124024709}
[B03 s0] ep 10 train_loss 0.0601 val_loss 0.1267 F1 0.9503 top1 0.9654 (33s)
QUEUE {"exp_id": "B03", "status": "ok", "val_macro_f1": 0.9502624553264576, "min": 6.7240373929341635}

```

### Execution (2026-10-05 03:43:18)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
[B02 s0] ep 10 train_loss 0.0433 val_loss 0.0953 F1 0.9661 top1 0.9749 (49s)
QUEUE {"exp_id": "B02", "status": "ok", "val_macro_f1": 0.9675884081376529, "min": 10.642984124024709}
[B03 s0] ep 10 train_loss 0.0601 val_loss 0.1267 F1 0.9503 top1 0.9654 (33s)
QUEUE {"exp_id": "B03", "status": "ok", "val_macro_f1": 0.9502624553264576, "min": 6.7240373929341635}

```

### Execution (2026-10-05 03:44:22)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
[B02 s0] ep 10 train_loss 0.0433 val_loss 0.0953 F1 0.9661 top1 0.9749 (49s)
QUEUE {"exp_id": "B02", "status": "ok", "val_macro_f1": 0.9675884081376529, "min": 10.642984124024709}
[B03 s0] ep 10 train_loss 0.0601 val_loss 0.1267 F1 0.9503 top1 0.9654 (33s)
QUEUE {"exp_id": "B03", "status": "ok", "val_macro_f1": 0.9502624553264576, "min": 6.7240373929341635}

```

### Execution (2026-10-05 03:45:25)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
[B02 s0] ep 10 train_loss 0.0433 val_loss 0.0953 F1 0.9661 top1 0.9749 (49s)
QUEUE {"exp_id": "B02", "status": "ok", "val_macro_f1": 0.9675884081376529, "min": 10.642984124024709}
[B03 s0] ep 10 train_loss 0.0601 val_loss 0.1267 F1 0.9503 top1 0.9654 (33s)
QUEUE {"exp_id": "B03", "status": "ok", "val_macro_f1": 0.9502624553264576, "min": 6.7240373929341635}

```

### Execution (2026-10-05 03:46:29)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
[B02 s0] ep 10 train_loss 0.0433 val_loss 0.0953 F1 0.9661 top1 0.9749 (49s)
QUEUE {"exp_id": "B02", "status": "ok", "val_macro_f1": 0.9675884081376529, "min": 10.642984124024709}
[B03 s0] ep 10 train_loss 0.0601 val_loss 0.1267 F1 0.9503 top1 0.9654 (33s)
QUEUE {"exp_id": "B03", "status": "ok", "val_macro_f1": 0.9502624553264576, "min": 6.7240373929341635}

```

### Execution (2026-10-05 03:47:32)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
[B02 s0] ep 10 train_loss 0.0433 val_loss 0.0953 F1 0.9661 top1 0.9749 (49s)
QUEUE {"exp_id": "B02", "status": "ok", "val_macro_f1": 0.9675884081376529, "min": 10.642984124024709}
[B03 s0] ep 10 train_loss 0.0601 val_loss 0.1267 F1 0.9503 top1 0.9654 (33s)
QUEUE {"exp_id": "B03", "status": "ok", "val_macro_f1": 0.9502624553264576, "min": 6.7240373929341635}

```

### Execution (2026-10-05 03:48:36)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
[B02 s0] ep 10 train_loss 0.0433 val_loss 0.0953 F1 0.9661 top1 0.9749 (49s)
QUEUE {"exp_id": "B02", "status": "ok", "val_macro_f1": 0.9675884081376529, "min": 10.642984124024709}
[B03 s0] ep 10 train_loss 0.0601 val_loss 0.1267 F1 0.9503 top1 0.9654 (33s)
QUEUE {"exp_id": "B03", "status": "ok", "val_macro_f1": 0.9502624553264576, "min": 6.7240373929341635}

```

### Execution (2026-10-05 03:49:39)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
[B02 s0] ep 10 train_loss 0.0433 val_loss 0.0953 F1 0.9661 top1 0.9749 (49s)
QUEUE {"exp_id": "B02", "status": "ok", "val_macro_f1": 0.9675884081376529, "min": 10.642984124024709}
[B03 s0] ep 10 train_loss 0.0601 val_loss 0.1267 F1 0.9503 top1 0.9654 (33s)
QUEUE {"exp_id": "B03", "status": "ok", "val_macro_f1": 0.9502624553264576, "min": 6.7240373929341635}
[B04 s0] ep 10 train_loss 0.0730 val_loss 0.1207 F1 0.9570 top1 0.9686 (62s)
QUEUE {"exp_id": "B04", "status": "ok", "val_macro_f1": 0.957506356825206, "min": 13.229557156562805}

```

### Execution (2026-10-05 03:50:43)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
[B02 s0] ep 10 train_loss 0.0433 val_loss 0.0953 F1 0.9661 top1 0.9749 (49s)
QUEUE {"exp_id": "B02", "status": "ok", "val_macro_f1": 0.9675884081376529, "min": 10.642984124024709}
[B03 s0] ep 10 train_loss 0.0601 val_loss 0.1267 F1 0.9503 top1 0.9654 (33s)
QUEUE {"exp_id": "B03", "status": "ok", "val_macro_f1": 0.9502624553264576, "min": 6.7240373929341635}
[B04 s0] ep 10 train_loss 0.0730 val_loss 0.1207 F1 0.9570 top1 0.9686 (62s)
QUEUE {"exp_id": "B04", "status": "ok", "val_macro_f1": 0.957506356825206, "min": 13.229557156562805}

```

### Execution (2026-10-05 03:51:46)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
[B02 s0] ep 10 train_loss 0.0433 val_loss 0.0953 F1 0.9661 top1 0.9749 (49s)
QUEUE {"exp_id": "B02", "status": "ok", "val_macro_f1": 0.9675884081376529, "min": 10.642984124024709}
[B03 s0] ep 10 train_loss 0.0601 val_loss 0.1267 F1 0.9503 top1 0.9654 (33s)
QUEUE {"exp_id": "B03", "status": "ok", "val_macro_f1": 0.9502624553264576, "min": 6.7240373929341635}
[B04 s0] ep 10 train_loss 0.0730 val_loss 0.1207 F1 0.9570 top1 0.9686 (62s)
QUEUE {"exp_id": "B04", "status": "ok", "val_macro_f1": 0.957506356825206, "min": 13.229557156562805}

```

### Execution (2026-10-05 03:52:50)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
[B02 s0] ep 10 train_loss 0.0433 val_loss 0.0953 F1 0.9661 top1 0.9749 (49s)
QUEUE {"exp_id": "B02", "status": "ok", "val_macro_f1": 0.9675884081376529, "min": 10.642984124024709}
[B03 s0] ep 10 train_loss 0.0601 val_loss 0.1267 F1 0.9503 top1 0.9654 (33s)
QUEUE {"exp_id": "B03", "status": "ok", "val_macro_f1": 0.9502624553264576, "min": 6.7240373929341635}
[B04 s0] ep 10 train_loss 0.0730 val_loss 0.1207 F1 0.9570 top1 0.9686 (62s)
QUEUE {"exp_id": "B04", "status": "ok", "val_macro_f1": 0.957506356825206, "min": 13.229557156562805}

```

### Execution (2026-10-05 03:53:53)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
[B02 s0] ep 10 train_loss 0.0433 val_loss 0.0953 F1 0.9661 top1 0.9749 (49s)
QUEUE {"exp_id": "B02", "status": "ok", "val_macro_f1": 0.9675884081376529, "min": 10.642984124024709}
[B03 s0] ep 10 train_loss 0.0601 val_loss 0.1267 F1 0.9503 top1 0.9654 (33s)
QUEUE {"exp_id": "B03", "status": "ok", "val_macro_f1": 0.9502624553264576, "min": 6.7240373929341635}
[B04 s0] ep 10 train_loss 0.0730 val_loss 0.1207 F1 0.9570 top1 0.9686 (62s)
QUEUE {"exp_id": "B04", "status": "ok", "val_macro_f1": 0.957506356825206, "min": 13.229557156562805}

```

### Execution (2026-10-05 03:54:57)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
[B02 s0] ep 10 train_loss 0.0433 val_loss 0.0953 F1 0.9661 top1 0.9749 (49s)
QUEUE {"exp_id": "B02", "status": "ok", "val_macro_f1": 0.9675884081376529, "min": 10.642984124024709}
[B03 s0] ep 10 train_loss 0.0601 val_loss 0.1267 F1 0.9503 top1 0.9654 (33s)
QUEUE {"exp_id": "B03", "status": "ok", "val_macro_f1": 0.9502624553264576, "min": 6.7240373929341635}
[B04 s0] ep 10 train_loss 0.0730 val_loss 0.1207 F1 0.9570 top1 0.9686 (62s)
QUEUE {"exp_id": "B04", "status": "ok", "val_macro_f1": 0.957506356825206, "min": 13.229557156562805}

```

### Execution (2026-10-05 03:56:00)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
[B02 s0] ep 10 train_loss 0.0433 val_loss 0.0953 F1 0.9661 top1 0.9749 (49s)
QUEUE {"exp_id": "B02", "status": "ok", "val_macro_f1": 0.9675884081376529, "min": 10.642984124024709}
[B03 s0] ep 10 train_loss 0.0601 val_loss 0.1267 F1 0.9503 top1 0.9654 (33s)
QUEUE {"exp_id": "B03", "status": "ok", "val_macro_f1": 0.9502624553264576, "min": 6.7240373929341635}
[B04 s0] ep 10 train_loss 0.0730 val_loss 0.1207 F1 0.9570 top1 0.9686 (62s)
QUEUE {"exp_id": "B04", "status": "ok", "val_macro_f1": 0.957506356825206, "min": 13.229557156562805}
[B05 s0] ep 10 train_loss 0.2632 val_loss 0.6501 F1 0.7077 top1 0.7892 (27s)
QUEUE {"exp_id": "B05", "status": "ok", "val_macro_f1": 0.7250973478010642, "min": 6.153886671861013}

```

### Execution (2026-10-05 03:57:04)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
[B02 s0] ep 10 train_loss 0.0433 val_loss 0.0953 F1 0.9661 top1 0.9749 (49s)
QUEUE {"exp_id": "B02", "status": "ok", "val_macro_f1": 0.9675884081376529, "min": 10.642984124024709}
[B03 s0] ep 10 train_loss 0.0601 val_loss 0.1267 F1 0.9503 top1 0.9654 (33s)
QUEUE {"exp_id": "B03", "status": "ok", "val_macro_f1": 0.9502624553264576, "min": 6.7240373929341635}
[B04 s0] ep 10 train_loss 0.0730 val_loss 0.1207 F1 0.9570 top1 0.9686 (62s)
QUEUE {"exp_id": "B04", "status": "ok", "val_macro_f1": 0.957506356825206, "min": 13.229557156562805}
[B05 s0] ep 10 train_loss 0.2632 val_loss 0.6501 F1 0.7077 top1 0.7892 (27s)
QUEUE {"exp_id": "B05", "status": "ok", "val_macro_f1": 0.7250973478010642, "min": 6.153886671861013}

```

### Execution (2026-10-05 03:58:07)
```python
import os
os.environ['SH'] = "grep -E 'QUEUE|Traceback|ep 10' logs/B02-B06.log"
import os, subprocess
print(subprocess.run(os.environ.get("SH", "tail -n 30 /content/lab/logs/*.log"), shell=True, capture_output=True, text=True, cwd="/content/lab").stdout)

```

**Output**:
```
[B02 s0] ep 10 train_loss 0.0433 val_loss 0.0953 F1 0.9661 top1 0.9749 (49s)
QUEUE {"exp_id": "B02", "status": "ok", "val_macro_f1": 0.9675884081376529, "min": 10.642984124024709}
[B03 s0] ep 10 train_loss 0.0601 val_loss 0.1267 F1 0.9503 top1 0.9654 (33s)
QUEUE {"exp_id": "B03", "status": "ok", "val_macro_f1": 0.9502624553264576, "min": 6.7240373929341635}
[B04 s0] ep 10 train_loss 0.0730 val_loss 0.1207 F1 0.9570 top1 0.9686 (62s)
QUEUE {"exp_id": "B04", "status": "ok", "val_macro_f1": 0.957506356825206, "min": 13.229557156562805}
[B05 s0] ep 10 train_loss 0.2632 val_loss 0.6501 F1 0.7077 top1 0.7892 (27s)
QUEUE {"exp_id": "B05", "status": "ok", "val_macro_f1": 0.7250973478010642, "min": 6.153886671861013}

```

