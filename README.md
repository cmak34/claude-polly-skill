# claude-polly-skill

A simple Claude Code skill for generating MP3 speech files from text using AWS Polly. Supports plain text and SSML, with auto-detection.

## Features

- 🗣️ Convert text to natural-sounding speech via AWS Polly
- 📝 Supports both plain text and SSML (auto-detected)
- 🌍 Multi-language support (English, Spanish, French, German, Japanese, Chinese, and more)
- ⏱️ Timestamp-based filenames to prevent overwriting
- 🔐 Credentials loaded securely from `.env`
- 🧩 Drop-in Claude Code skill or standalone CLI

## Installation

### Where to Clone

**As a Claude Code Skill (recommended):**
```bash
git clone https://github.com/cmak34/claude-polly-skill.git ~/.claude/skills/claude-polly-skill
cd ~/.claude/skills/claude-polly-skill
```

Claude Code auto-discovers the skill via the included `SKILL.md`.

**As a Standalone CLI:** Clone anywhere you like and `cd` into it.

### Install

Pick one of the methods below. After installation, the `polly` command is available globally (except for Option D).

#### Option A: pipx (recommended — isolated global install)

[pipx](https://pipx.pypa.io/) installs Python CLI tools in isolated environments so they don't pollute your global Python:

```bash
pipx install .
```

Then run from anywhere:

```bash
polly generate "Hello" --voice Joanna --language en-US
```

To update: `pipx reinstall claude-polly-skill`

#### Option B: uv (fastest — Rust-based)

[uv](https://github.com/astral-sh/uv) is a modern Rust-based Python package manager:

```bash
# Install uv once
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install the tool globally
uv tool install .
```

Run from anywhere:

```bash
polly generate "Hello" --voice Joanna --language en-US
```

Or for ephemeral use (no install):

```bash
uv run polly.py generate "Hello" --voice Joanna --language en-US
```

#### Option C: venv + pip (classic Python)

```bash
python3 -m venv .venv
source .venv/bin/activate          # macOS/Linux
# .venv\Scripts\activate           # Windows
pip install -e .
```

Run:
```bash
polly generate "Hello" --voice Joanna --language en-US
```

#### Option D: Global pip (simplest, but pollutes global Python)

```bash
pip install .
polly generate "Hello" --voice Joanna --language en-US
```

Or, without installing (run as a script):

```bash
pip install -r requirements.txt
python polly.py generate "Hello" --voice Joanna --language en-US
```

## Setup

### 1. Create an AWS IAM User

1. Log in to the AWS Console
2. Navigate to **IAM → Users → Add user**
3. Grant the `AmazonPollyFullAccess` (or `AmazonPollyReadOnlyAccess`) policy
4. Create an **Access Key** under *Security credentials*
5. Save both the Access Key ID and Secret Access Key

### 2. Configure Credentials

```bash
cp .env.example .env
```

Edit `.env` with your AWS credentials:

```
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=your-secret-key-here
AWS_REGION=us-east-1
```

### 3. Verify Installation

```bash
python polly.py generate "Hello world" --voice Joanna --language en-US
```

You should see:
```
Success! Audio saved to: /path/to/output/polly_YYYYMMDD_HHMMSS.mp3
```

## Usage

### Basic Syntax

```bash
python polly.py generate "<TEXT>" --voice <VOICE_ID> --language <LANGUAGE_CODE> [--output-dir <PATH>]
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `<TEXT>` | Yes | Text to synthesize (plain text or SSML, max 3000 chars) |
| `--voice` | Yes | AWS voice ID (e.g., `Joanna`, `Matthew`) |
| `--language` | Yes | Language code (e.g., `en-US`, `es-ES`) |
| `--output-dir` | No | Output directory (default: `./output`) |

### Examples

**English:**
```bash
python polly.py generate "Welcome to the podcast" --voice Joanna --language en-US
```

**Spanish:**
```bash
python polly.py generate "Hola, ¿cómo estás?" --voice Lucia --language es-ES
```

**French:**
```bash
python polly.py generate "Bonjour le monde" --voice Celine --language fr-FR
```

**SSML (auto-detected when text starts with `<speak>`):**
```bash
python polly.py generate '<speak>Hello <break time="1s"/> <prosody rate="slow">world</prosody></speak>' --voice Joanna --language en-US
```

**Custom output directory:**
```bash
python polly.py generate "Hello" --voice Joanna --language en-US --output-dir /tmp/audio/
```

## Output Files & Cleanup

### Where MP3s are saved

By default, generated files go to `./output/` **relative to your current working directory** — not the skill's install directory. For example:

```bash
cd ~/my-project
polly generate "Hello" --voice Joanna --language en-US
# → ~/my-project/output/polly_20260415_150000.mp3
```

Use `--output-dir` to override:

```bash
polly generate "Hello" --voice Joanna --language en-US --output-dir ~/audio-library
```

### File naming

Files are named `polly_YYYYMMDD_HHMMSS.mp3` based on the generation timestamp. They accumulate — the script never overwrites existing files, but it also never auto-deletes them.

### Cleaning up old files

Use the built-in `cleanup` command:

```bash
# Delete ALL polly_*.mp3 files in ./output/
polly cleanup

# Delete only files older than 7 days
polly cleanup --older-than-days 7

# Preview what would be deleted (safe)
polly cleanup --dry-run

# Clean a specific directory
polly cleanup --output-dir /path/to/audio

# Combine flags
polly cleanup --output-dir ~/my-project/output --older-than-days 30 --dry-run
```

The `cleanup` command only touches files matching the `polly_*.mp3` pattern, so other files in the directory are safe.

### Manual cleanup (if you prefer shell)

```bash
# Delete all
rm output/polly_*.mp3

# Delete files older than 7 days
find output/ -name "polly_*.mp3" -mtime +7 -delete
```

## SSML Support

Supply text wrapped in `<speak>` tags to use [AWS Polly SSML](https://docs.aws.amazon.com/polly/latest/dg/supportedtags.html):

```xml
<speak>
  Hello <break time="1s"/> world.
  <prosody rate="slow">This is slow.</prosody>
  <emphasis level="strong">This is emphasized.</emphasis>
  <say-as interpret-as="spell-out">AWS</say-as>
</speak>
```

Common SSML tags:
- `<break time="Xs"/>` — pause for X seconds
- `<prosody rate="slow|medium|fast">` — change speaking rate
- `<emphasis level="strong|moderate|reduced">` — emphasize text
- `<say-as interpret-as="spell-out|number|date">` — pronunciation hints

## Available Voices

Common neural voices by language:

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

Full list: [AWS Polly Voice Reference](https://docs.aws.amazon.com/polly/latest/dg/voicelist.html)

## Using with Claude Code

This skill is primarily designed for Claude Code. Once installed at `~/.claude/skills/claude-polly-skill/` (see Installation above), Claude Code auto-discovers it via the included `SKILL.md`. Just ask:

> *"Use the polly skill to generate speech for 'Hello World' using Joanna's voice"*

Claude will invoke the CLI and return the generated MP3 path.

> **Other AI coding agents:** Since `polly` is a standard CLI once installed (`pipx install .`), it may also work with other shell-enabled AI assistants such as OpenCode, Cursor, Aider, Continue, Codex CLI, or GitHub Copilot CLI. The `SKILL.md` auto-discovery is Claude Code-specific, but the CLI itself is tool-agnostic — just point your assistant at `polly --help` and it can invoke commands directly.

## Troubleshooting

### `.env file not found`
Create a `.env` file in the project root with your AWS credentials. Use `.env.example` as a template.

### `Missing required credentials in .env`
Ensure both `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are set.

### `Voice 'X' not found`
Check the voice ID is correct for the given language. See the voice list above.

### `Text exceeds 3000 character limit`
Split the text into chunks of 3000 characters or fewer. AWS Polly enforces this per request.

### `AccessDeniedException`
Your IAM user does not have Polly permissions. Attach `AmazonPollyFullAccess` or `AmazonPollyReadOnlyAccess`.

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Project Structure

```
claude-polly-skill/
├── polly.py              # Main CLI script
├── requirements.txt      # Python dependencies
├── .env.example          # Credentials template
├── SKILL.md              # Claude Code skill manifest
├── README.md             # This file
├── LICENSE               # MIT License
└── tests/
    └── test_polly.py     # Test suite
```

### Dependencies

- `boto3` — AWS SDK for Python
- `click` — CLI framework
- `python-dotenv` — Environment variable loader

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Add tests for new functionality
4. Ensure all tests pass (`pytest tests/`)
5. Submit a pull request

## License

MIT License — see [LICENSE](LICENSE) for details.

## Author

**Hugo Mak** — [cmak34@centennialcollege.ca](mailto:cmak34@centennialcollege.ca)

## Acknowledgments

- [AWS Polly](https://aws.amazon.com/polly/) for the text-to-speech service
- [Anthropic Claude Code](https://claude.com/claude-code) for the skill integration framework
