---
name: claude-polly-skill
description: Generate MP3 speech from text using AWS Polly. Use when user wants text-to-speech (TTS), voice generation, audio narration, or to convert text into spoken audio files. Supports plain text and SSML markup (auto-detected when text starts with <speak>).
---

# claude-polly-skill — AWS Text-to-Speech

Generates MP3 audio files from text using AWS Polly. Plain text and SSML are both supported (SSML auto-detected when text begins with `<speak>`).

## Invocation

If installed via `pipx install .` or `uv tool install .`, the `polly` command is available globally:

```bash
polly generate "<TEXT>" --voice <VOICE_ID> --language <LANGUAGE_CODE>
```

Otherwise, run the script directly from the skill directory:

```bash
# From skill directory
python polly.py generate "<TEXT>" --voice <VOICE_ID> --language <LANGUAGE_CODE>

# Using uv (no install needed)
uv run polly.py generate "<TEXT>" --voice <VOICE_ID> --language <LANGUAGE_CODE>

# Using venv
.venv/bin/python polly.py generate "<TEXT>" --voice <VOICE_ID> --language <LANGUAGE_CODE>
```

Output files are saved to `./output/` relative to the current directory, with timestamp-based names like `polly_YYYYMMDD_HHMMSS.mp3`. Use `--output-dir <PATH>` to override.

## Parameters

- `<TEXT>` (required) — Text to convert to speech (max 3000 characters). Wrap in `<speak>...</speak>` to use SSML.
- `--voice` (required) — AWS voice ID
- `--language` (required) — Language code
- `--output-dir` (optional) — Custom output directory (default: `./output`)

## Common Voices by Language

| Language | Code | Voices |
|----------|------|--------|
| English (US) | `en-US` | Joanna, Matthew, Joey, Justin, Kimberly, Kevin, Salli |
| English (GB) | `en-GB` | Amy, Brian, Emma |
| Spanish (ES) | `es-ES` | Conchita, Enrique, Lucia |
| Spanish (MX) | `es-MX` | Mia |
| French (FR) | `fr-FR` | Celine, Mathieu, Lea |
| German (DE) | `de-DE` | Hans, Marlene, Vicki |
| Italian (IT) | `it-IT` | Carla, Giorgio, Bianca |
| Portuguese (BR) | `pt-BR` | Vitoria, Ricardo, Camila |
| Japanese | `ja-JP` | Mizuki, Takumi |
| Korean | `ko-KR` | Seoyeon |
| Mandarin | `cmn-CN` | Zhiyu |

Full list: https://docs.aws.amazon.com/polly/latest/dg/voicelist.html

## Examples

```bash
# Plain text
python polly.py generate "Welcome to the podcast" --voice Joanna --language en-US

# SSML (auto-detected)
python polly.py generate '<speak>Hello <break time="1s"/> <prosody rate="slow">world</prosody></speak>' --voice Joanna --language en-US

# Spanish
python polly.py generate "Hola mundo" --voice Lucia --language es-ES

# Custom output location
python polly.py generate "Hello" --voice Joanna --language en-US --output-dir /tmp/audio/
```

## Configuration

Requires `.env` file in the skill root directory with:

```
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
AWS_REGION=us-east-1
```

The IAM user needs `AmazonPollyFullAccess` (or the read-only variant).

## Output

On success, the script prints the full path to the generated MP3 file:

```
Success! Audio saved to: /path/to/output/polly_20260415_143501.mp3
```

Files accumulate in `./output/` (or the directory specified by `--output-dir`) with timestamp-based names. They are never overwritten or auto-deleted.

## Cleanup

To delete generated MP3 files, use the `cleanup` subcommand:

```bash
polly cleanup                                  # delete all polly_*.mp3 in ./output/
polly cleanup --older-than-days 7              # delete files older than 7 days
polly cleanup --dry-run                        # preview without deleting
polly cleanup --output-dir /path/to/audio      # custom directory
```

Only files matching `polly_*.mp3` are touched — other files are safe.

**When to suggest cleanup to the user:**
- If generating many files in one session, offer to clean up old ones at the end
- If the user reports their project has lots of audio files they no longer need
- Before committing a project — remind the user that `output/` is gitignored by default but old MP3s may exist
