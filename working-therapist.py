import gradio as gr
from pathlib import Path
import openai, config, subprocess
import os
openai.api_key = config.OPENAI_API_KEY

messages = [{"role": "system", "content": 'You are a therapist. Respond to all input in 25 words or less.'}]

def transcribe(audio):
    global messages

    audio_filename_with_extension = audio + '.wav'
    os.rename(audio, audio_filename_with_extension)
    
    audio_file = open(audio_filename_with_extension, "rb")
    transcript = openai.audio.transcriptions.create(model= "whisper-1", file= audio_file)

    transcript_text = transcript.text
    messages.append({"role": "user", "content": transcript_text})

    response = openai.chat.completions.create(model="gpt-3.5-turbo", messages=messages)

    print("Response: ", response)
    system_message = response.choices[0].message
    messages.append({"role": system_message.role, "content": system_message.content})
   
    response_tts = openai.audio.speech.create(
      model="tts-1",
      voice="alloy",
      input=system_message.content
    )
    speech_file_path = Path(__file__).parent / "speech.mp3"
    response_tts.stream_to_file(speech_file_path)

    return speech_file_path


ui = gr.Interface(fn=transcribe, inputs=gr.Audio(sources="microphone", type="filepath"), outputs="audio")
ui.launch()

       
