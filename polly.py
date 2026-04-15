# polly/polly.py
import click
import os
from pathlib import Path
from dotenv import load_dotenv
import sys
import boto3
from datetime import datetime

def load_credentials():
    """Load AWS credentials from .env file"""
    env_path = Path(__file__).parent / '.env'

    if not env_path.exists():
        click.echo(
            f"Error: .env file not found at {env_path}\n"
            f"Please create .env with AWS credentials. "
            f"See .env.example for template.",
            err=True
        )
        sys.exit(1)

    load_dotenv(env_path)

    required_keys = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
    missing_keys = [key for key in required_keys if not os.getenv(key)]

    if missing_keys:
        click.echo(
            f"Error: Missing required credentials in .env: {', '.join(missing_keys)}",
            err=True
        )
        sys.exit(1)

def synthesize_and_save(text, voice, language, output_dir):
    """Call Polly API and save audio to file"""

    # Validate text is not empty
    if len(text) == 0:
        click.echo("Error: Text cannot be empty", err=True)
        sys.exit(1)

    # Validate text length (AWS Polly limit)
    if len(text) > 3000:
        click.echo(
            f"Error: Text exceeds 3000 character limit ({len(text)} chars). "
            f"Please split into smaller chunks.",
            err=True
        )
        sys.exit(1)

    # Initialize Polly client
    polly_client = boto3.client(
        'polly',
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )

    # Auto-detect SSML: if text starts with <speak>, treat as SSML
    text_type = 'ssml' if text.strip().startswith('<speak') else 'text'

    try:
        # Call Polly SynthesizeSpeech
        response = polly_client.synthesize_speech(
            Text=text,
            TextType=text_type,
            OutputFormat='mp3',
            VoiceId=voice,
            LanguageCode=language
        )
    except Exception as e:
        click.echo(f"Error calling AWS Polly: {str(e)}", err=True)
        sys.exit(1)

    # Generate timestamped filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'polly_{timestamp}.mp3'
    filepath = Path(output_dir) / filename

    # Write audio stream to file
    try:
        with open(filepath, 'wb') as f:
            f.write(response['AudioStream'].read())
        return filepath
    except Exception as e:
        click.echo(f"Error writing audio file: {str(e)}", err=True)
        sys.exit(1)

@click.group()
def cli():
    """AWS Polly Text-to-Speech CLI"""
    pass

@cli.command()
@click.argument('text')
@click.option('--voice', required=True, help='AWS voice ID (e.g., Joanna, Matthew)')
@click.option('--language', required=True, help='Language code (e.g., en-US, es-ES)')
@click.option('--output-dir', default='./output', help='Output directory for MP3 files')
def generate(text, voice, language, output_dir):
    """Generate speech from text using AWS Polly"""
    load_credentials()

    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Synthesize and save
    filepath = synthesize_and_save(text, voice, language, str(output_path))

    click.echo(f"Success! Audio saved to: {filepath.resolve()}")

@cli.command()
@click.option('--output-dir', default='./output', help='Directory to clean (default: ./output)')
@click.option('--older-than-days', type=int, default=None, help='Only delete files older than N days')
@click.option('--dry-run', is_flag=True, help='Show what would be deleted without deleting')
def cleanup(output_dir, older_than_days, dry_run):
    """Delete generated polly_*.mp3 files from the output directory"""
    output_path = Path(output_dir)

    if not output_path.exists():
        click.echo(f"Directory does not exist: {output_path}")
        return

    files = sorted(output_path.glob('polly_*.mp3'))

    if older_than_days is not None:
        cutoff = datetime.now().timestamp() - (older_than_days * 86400)
        files = [f for f in files if f.stat().st_mtime < cutoff]

    if not files:
        click.echo("No matching files to clean up.")
        return

    total_size = sum(f.stat().st_size for f in files)
    size_kb = total_size / 1024

    action = "Would delete" if dry_run else "Deleting"
    click.echo(f"{action} {len(files)} file(s) ({size_kb:.1f} KB):")
    for f in files:
        click.echo(f"  {f.name}")
        if not dry_run:
            f.unlink()

    if not dry_run:
        click.echo(f"Freed {size_kb:.1f} KB")

if __name__ == '__main__':
    cli()
