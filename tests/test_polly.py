# tests/test_polly.py
import os
import pytest
import tempfile
from pathlib import Path
from dotenv import load_dotenv
from unittest.mock import patch, MagicMock
from datetime import datetime

def test_env_file_loads_credentials():
    """Test that .env file loads AWS credentials"""
    # Create a temporary .env file for testing
    env_path = Path("/Users/kr/kr/polly/.env.test")
    env_path.write_text(
        "AWS_ACCESS_KEY_ID=test-key\n"
        "AWS_SECRET_ACCESS_KEY=test-secret\n"
        "AWS_REGION=us-west-2\n"
    )

    # Load the test env file
    load_dotenv(env_path)

    # Verify credentials are loaded
    assert os.getenv("AWS_ACCESS_KEY_ID") == "test-key"
    assert os.getenv("AWS_SECRET_ACCESS_KEY") == "test-secret"
    assert os.getenv("AWS_REGION") == "us-west-2"

    # Cleanup
    env_path.unlink()

def test_env_file_missing_raises_error():
    """Test that missing .env file gives helpful error"""
    # We'll implement this after the polly.py module exists
    pass

from click.testing import CliRunner
from polly import cli

def test_generate_command_requires_voice():
    """Test that --voice is required"""
    runner = CliRunner()
    result = runner.invoke(cli, ['generate', 'Hello world', '--language', 'en-US'])
    assert result.exit_code == 2  # Click error for missing required option
    assert 'Missing option' in result.output or 'voice' in result.output.lower()

def test_generate_command_requires_language():
    """Test that --language is required"""
    runner = CliRunner()
    result = runner.invoke(cli, ['generate', 'Hello world', '--voice', 'Joanna'])
    assert result.exit_code == 2
    assert 'Missing option' in result.output or 'language' in result.output.lower()

def test_generate_command_accepts_valid_args():
    """Test that command accepts valid arguments"""
    runner = CliRunner()
    with patch('polly.boto3.client') as mock_boto:
        # Setup mock Polly response
        mock_polly = MagicMock()
        mock_boto.return_value = mock_polly
        mock_response = {
            'AudioStream': MagicMock(read=MagicMock(return_value=b'fake-mp3-data'))
        }
        mock_polly.synthesize_speech.return_value = mock_response

        result = runner.invoke(cli, [
            'generate',
            'Hello world',
            '--voice', 'Joanna',
            '--language', 'en-US'
        ])
        assert result.exit_code == 0
        assert 'Success!' in result.output

def test_generate_command_custom_output_dir():
    """Test that --output-dir can be specified"""
    runner = CliRunner()
    with patch('polly.boto3.client') as mock_boto:
        # Setup mock Polly response
        mock_polly = MagicMock()
        mock_boto.return_value = mock_polly
        mock_response = {
            'AudioStream': MagicMock(read=MagicMock(return_value=b'fake-mp3-data'))
        }
        mock_polly.synthesize_speech.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmpdir:
            custom_path = Path(tmpdir) / 'custom_output'
            result = runner.invoke(cli, [
                'generate',
                'Hello',
                '--voice', 'Joanna',
                '--language', 'en-US',
                '--output-dir', str(custom_path)
            ])
            assert result.exit_code == 0
            assert str(custom_path.resolve()) in result.output

def test_output_directory_created_if_missing():
    """Test that output directory is auto-created"""
    runner = CliRunner()
    with patch('polly.boto3.client') as mock_boto:
        # Setup mock Polly response
        mock_polly = MagicMock()
        mock_boto.return_value = mock_polly
        mock_response = {
            'AudioStream': MagicMock(read=MagicMock(return_value=b'fake-mp3-data'))
        }
        mock_polly.synthesize_speech.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / 'new_output'
            assert not output_dir.exists()

            result = runner.invoke(cli, [
                'generate',
                'test',
                '--voice', 'Joanna',
                '--language', 'en-US',
                '--output-dir', str(output_dir)
            ])

            # Directory should be created
            assert output_dir.exists()

def test_audio_file_saved_with_timestamp_name():
    """Test that audio file is saved with correct timestamp format"""
    runner = CliRunner()

    # Mock boto3 and the Polly API
    with patch('polly.boto3.client') as mock_boto:
        # Setup mock Polly response
        mock_polly = MagicMock()
        mock_boto.return_value = mock_polly

        # Mock the SynthesizeSpeech response with audio stream
        mock_response = {
            'AudioStream': MagicMock(read=MagicMock(return_value=b'fake-mp3-data'))
        }
        mock_polly.synthesize_speech.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmpdir:
            result = runner.invoke(cli, [
                'generate',
                'Hello',
                '--voice', 'Joanna',
                '--language', 'en-US',
                '--output-dir', tmpdir
            ])

            # Check that file was created
            files = list(Path(tmpdir).glob('polly_*.mp3'))
            assert len(files) == 1
            assert files[0].read_bytes() == b'fake-mp3-data'

def test_polly_invalid_voice_error():
    """Test error handling for invalid voice"""
    runner = CliRunner()

    with patch('polly.boto3.client') as mock_boto:
        mock_polly = MagicMock()
        mock_boto.return_value = mock_polly

        # Simulate Polly error
        mock_polly.synthesize_speech.side_effect = Exception(
            "Voice 'InvalidVoice' not found"
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            result = runner.invoke(cli, [
                'generate',
                'test',
                '--voice', 'InvalidVoice',
                '--language', 'en-US',
                '--output-dir', tmpdir
            ])

            assert result.exit_code == 1
            assert 'Error calling AWS Polly' in result.output

def test_text_length_validation():
    """Test that very long text is rejected"""
    runner = CliRunner()
    long_text = 'word ' * 1000  # ~5000 characters

    with tempfile.TemporaryDirectory() as tmpdir:
        result = runner.invoke(cli, [
            'generate',
            long_text,
            '--voice', 'Joanna',
            '--language', 'en-US',
            '--output-dir', tmpdir
        ])

        assert result.exit_code == 1
        assert 'Text exceeds 3000 character limit' in result.output

def test_empty_text_validation():
    """Test that empty text is rejected"""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        result = runner.invoke(cli, [
            'generate',
            '',
            '--voice', 'Joanna',
            '--language', 'en-US',
            '--output-dir', tmpdir
        ])

        assert result.exit_code == 1


def test_ssml_auto_detected_when_text_starts_with_speak_tag():
    """Test that SSML is auto-detected when text begins with <speak>"""
    from polly import cli
    from click.testing import CliRunner
    runner = CliRunner()

    with patch('polly.boto3.client') as mock_boto:
        mock_polly = MagicMock()
        mock_boto.return_value = mock_polly
        mock_polly.synthesize_speech.return_value = {
            'AudioStream': MagicMock(read=MagicMock(return_value=b'fake-mp3-data'))
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            ssml_text = '<speak>Hello <break time="1s"/> world</speak>'
            runner.invoke(cli, [
                'generate', ssml_text,
                '--voice', 'Joanna', '--language', 'en-US',
                '--output-dir', tmpdir
            ])

            # Verify TextType='ssml' was passed
            call_kwargs = mock_polly.synthesize_speech.call_args.kwargs
            assert call_kwargs['TextType'] == 'ssml'


def test_plain_text_uses_text_type():
    """Test that plain text uses TextType='text'"""
    from polly import cli
    from click.testing import CliRunner
    runner = CliRunner()

    with patch('polly.boto3.client') as mock_boto:
        mock_polly = MagicMock()
        mock_boto.return_value = mock_polly
        mock_polly.synthesize_speech.return_value = {
            'AudioStream': MagicMock(read=MagicMock(return_value=b'fake-mp3-data'))
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(cli, [
                'generate', 'Plain hello',
                '--voice', 'Joanna', '--language', 'en-US',
                '--output-dir', tmpdir
            ])

            call_kwargs = mock_polly.synthesize_speech.call_args.kwargs
            assert call_kwargs['TextType'] == 'text'


def test_cleanup_deletes_all_polly_files():
    """Test that cleanup removes polly_*.mp3 files"""
    from polly import cli
    from click.testing import CliRunner
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create fake polly files
        for i in range(3):
            (Path(tmpdir) / f'polly_2026041{i}_120000.mp3').write_bytes(b'fake')
        # Create a non-polly file that should NOT be deleted
        (Path(tmpdir) / 'keep_me.mp3').write_bytes(b'keep')

        result = runner.invoke(cli, ['cleanup', '--output-dir', tmpdir])

        assert result.exit_code == 0
        assert 'Deleting 3' in result.output

        # Verify polly files gone, other file remains
        remaining = list(Path(tmpdir).iterdir())
        assert len(remaining) == 1
        assert remaining[0].name == 'keep_me.mp3'


def test_cleanup_dry_run_does_not_delete():
    """Test that --dry-run shows files but doesn't delete them"""
    from polly import cli
    from click.testing import CliRunner
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / 'polly_20260415_120000.mp3').write_bytes(b'fake')

        result = runner.invoke(cli, ['cleanup', '--output-dir', tmpdir, '--dry-run'])

        assert result.exit_code == 0
        assert 'Would delete' in result.output

        # File should still exist
        assert (Path(tmpdir) / 'polly_20260415_120000.mp3').exists()


def test_cleanup_older_than_days_filter():
    """Test that --older-than-days only deletes old files"""
    import time
    from polly import cli
    from click.testing import CliRunner
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        # New file - should NOT be deleted
        new_file = Path(tmpdir) / 'polly_20260415_120000.mp3'
        new_file.write_bytes(b'new')

        # Old file - backdated 10 days
        old_file = Path(tmpdir) / 'polly_20260405_120000.mp3'
        old_file.write_bytes(b'old')
        ten_days_ago = time.time() - (10 * 86400)
        os.utime(old_file, (ten_days_ago, ten_days_ago))

        result = runner.invoke(cli, ['cleanup', '--output-dir', tmpdir, '--older-than-days', '7'])

        assert result.exit_code == 0
        assert new_file.exists()
        assert not old_file.exists()


def test_cleanup_empty_directory():
    """Test cleanup on empty directory shows friendly message"""
    from polly import cli
    from click.testing import CliRunner
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        result = runner.invoke(cli, ['cleanup', '--output-dir', tmpdir])

        assert result.exit_code == 0
        assert 'No matching files' in result.output
