import os
import subprocess


def convert_to_mp3(input_file_path: str) -> str:
    if input_file_path.lower().endswith('.mp3'):
        return input_file_path
    output_file_path = os.path.splitext(input_file_path)[0] + '.mp3'
    # ffmpeg detects the input format from the content, so any audio WhatsApp sends (ogg/opus, aac, amr, mp4) works.
    subprocess.run(
        ['ffmpeg', '-y', '-loglevel', 'error', '-i', input_file_path, '-vn', '-ac', '1', '-b:a', '64k',
         output_file_path],
        check=True,
    )
    return output_file_path
