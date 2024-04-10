import whisper
from pydub import AudioSegment
from pydub.silence import split_on_silence

from openai_wrapper.chat import process_transcription


def split_audio_on_silence(audio_file_path: str, min_silence_len: int = 1000, silence_thresh: int = -40) -> list:
    """
    Splits the audio file into segments based on silence.
    :param audio_file_path: Path to the audio file.
    :param min_silence_len: Minimum length of a silence to be used for splitting.
    :param silence_thresh: The silence threshold in dB.
    :return: A list of AudioSegment instances representing the segments.
    """
    ext = audio_file_path.split('.')[-1]
    sound = AudioSegment.from_file(audio_file_path, format=ext)
    return split_on_silence(sound, min_silence_len=min_silence_len, silence_thresh=silence_thresh)


def split_audio_fixed_intervals(audio_file_path: str, interval_length: int) -> list:
    """
    Splits the audio file into fixed intervals.
    :param audio_file_path: Path to the audio file.
    :param interval_length: Length of each interval in milliseconds.
    :return: A list of AudioSegment instances representing the segments.
    """
    ext = audio_file_path.split('.')[-1]
    sound = AudioSegment.from_file(audio_file_path, format=ext)
    return [sound[i:i + interval_length] for i in range(0, len(sound), interval_length)]


def split_audio(audio_file_path: str, split_method: str = 'silence', audio_length_threshold: int = 60 * 1000,
                interval_length: int = 2 * 60 * 1000) -> list:
    ext = audio_file_path.split('.')[-1]
    sound = AudioSegment.from_file(audio_file_path, format=ext)
    if len(sound) > audio_length_threshold:
        if split_method == 'silence':
            segments = split_audio_on_silence(audio_file_path)
        elif split_method == 'fixed':
            segments = split_audio_fixed_intervals(audio_file_path, interval_length)
        else:
            raise ValueError(f"Invalid split method '{split_method}'")
    else:
        segments = [sound]

    return segments


def transcribe_audio(audio_file_path: str, **kwargs) -> str:
    model = whisper.load_model("base")
    result = model.transcribe(audio_file_path, **kwargs)
    ret = result['text']
    return ret


def transcribe_segments(segments: list, ext: str) -> str:
    """
    Transcribes a list of audio segments.
    :param segments: List of AudioSegment instances.
    :param ext: Format to export the segments before transcription.
    :return: Combined transcription text.
    """
    full_transcript = []
    for segment in segments:
        segment.export("temp_segment." + ext, format=ext)
        segment_text = transcribe_audio("temp_segment." + ext)
        full_transcript.append(segment_text)
    return ' '.join(full_transcript)


def speech_to_text(audio_file_path: str, split_method: str = None, retries: int = 0,
                   further_processing: bool = False) -> str:
    if split_method:
        segments = split_audio(audio_file_path, split_method=split_method)
        ext = audio_file_path.split('.')[-1]
        text = transcribe_segments(segments, ext)
    else:
        text = transcribe_audio(audio_file_path)
        previous_texts = [text]
        for i in range(retries):
            previous_texts_str = '\n'.join([f"{i + 1}. {t}" for i, t in enumerate(previous_texts)])
            initial_prompt = (f"This are the first attempts to transcribe the audio file:\n"
                              f"{previous_texts_str}\n\n"
                              f"Please use it to improve the transcription.")
            text = transcribe_audio(audio_file_path, initial_prompt=initial_prompt)
            previous_texts.append(text)
    if further_processing:
        correction, summary = process_transcription(text)
        text = f"*ORIGINAL TRANSCRIPTION:*\n{text}\n\n*CORRECTION:*\n{correction}\n\n*SUMMARY:*\n{summary}"
    return text


if __name__ == '__main__':
    print(speech_to_text('/Users/av/Downloads/test.mp3'))
