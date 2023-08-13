import os
import deepgram
import openai
from anvil.tables import app_tables

# Initialize Deepgram client
dg_client = deepgram.Client(api_key=os.getenv('DEEPGRAM_API_KEY'))

# Initialize OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')

# Transcription function
def transcribe_audio(audio_source, is_live=False, use_diarization=True, use_smart_formatting=True):
    try:
        options = {'punctuate': use_smart_formatting, 'diarize': use_diarization}
        if is_live:
            result = dg_client.transcription.stream(audio_source, **options)
        else:
            result = dg_client.transcription.transcribe(audio_source, **options)
        return result['transcript']
    except Exception as e:
        print(f"Error in transcribing audio: {e}")
        return None

# Refactored LLM function
def perform_llm_task(transcription, task_description):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            temperature=0,
            messages=[
                {"role": "system", "content": task_description},
                {"role": "user", "content": transcription}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error in performing LLM task: {e}")
        return None

# Refactored main function
def process_audio(audio_source, is_live=False, use_diarization=True, use_smart_formatting=True):
    transcription = transcribe_audio(audio_source, is_live, use_diarization, use_smart_formatting)
    if transcription is None:
        return None

    task_descriptions = {
        'summary': "You are a highly skilled AI trained in language comprehension and summarization...",
        'key_points': "You are a proficient AI with a specialty in distilling information into key points...",
        'action_items': "You are an AI expert in analyzing conversations and extracting action items...",
        'sentiment': "As an AI with expertise in language and emotion analysis, your task is to analyze the sentiment..."
    }
    results = {task: perform_llm_task(transcription, description) for task, description in task_descriptions.items()}

    try:
        app_tables.transcriptions.add_row(transcription=transcription, **results)
    except Exception as e:
        print(f"Error in saving results to Anvil Data Table: {e}")
        return None

    return {'transcription': transcription, **results}