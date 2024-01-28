# ai_functions.py
import openai, config
import os
from pathlib import Path

# Assuming you have your OpenAI API key set in your environment variables or config file
openai.api_key = config.OPENAI_API_KEY

def transcribe_audio(audio_path):
    with open(audio_path, "rb") as audio_file:
        transcript = openai.audio.transcriptions.create(model="whisper-1", file=audio_file)
    return transcript.text

def generate_response(transcript_text, messages):
    messages.append({"role": "user", "content": transcript_text})
    response = openai.chat.completions.create(model="gpt-4-turbo-preview", messages=messages)
    system_message = response.choices[0].message
    messages.append({"role": system_message.role, "content": system_message.content})
    return system_message.content

def convert_text_to_speech(text):
    response_tts = openai.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    speech_file_path = Path(__file__).parent / "speech.mp3"
    response_tts.stream_to_file(speech_file_path)
    return speech_file_path

def debrief_assistant(messages):
    # Create a new message with the role 'system' and content 'Summarize the conversation.'
    messages.append({"role": "system", 
                     "content": 
                             "Mission: You are an expert job candidate evaluator. You review the user responses to assistant's interview questions and make a recommendation of hire or no-hire.  \n" +
                            "Context:\n" +
                                "You read the assistant interview questions and read candidate responses. \n\n" +
                           "Persona:\n" +
                               "You are a tough evaluator \n" +
                                "You are known to hire only the best of the best candidates \n" +
                                "You have a high bar for an interview performance \n\n" +
                            "Instructions:\n" +
                                "You recommend a hire  or no hire decision \n" +
                                "You write a detailed summary, you include specific deatils where candidates did well and where can improve, you include details from their interview. \n" +
                                "You look for structure in responses, organized thoughts, concrete details \n" +
                                "you look for creative ideas and responses for case questions\n" +
                                "you look for depth and leadership \n" +
                                "you look for depth in metrics and product execution \n" +
                                "you look for strong previous experiences where they excelled at prior roles and solved tough problems\n\n" +
                            "Output:\n" +
                                "Your output should include 3 parts: Hire or no-hire recommendation, did well, could improve \n"
                     })

    # Send the messages to the ChatGPT model
    response = openai.chat.completions.create(model="gpt-4-turbo-preview", messages=messages)

    # Get the assistant's response
    summary = response.choices[0].message.content

    return summary