import gradio as gr
import speech_recognition as sr
import os
from gtts import gTTS
import tempfile

def summarize_document(file):
    return "This is a placeholder summary. Replace this with actual summary logic."

def summary_text_to_speech(summary_text):
    if not summary_text or summary_text.strip() == "":
        return None
    tts = gTTS(text=summary_text, lang='en')
    audio_path = "summary_tts.mp3"
    tts.save(audio_path)
    return audio_path

def handle_file_upload(file, file_count):
    file_name = os.path.basename(file.name) if hasattr(file, "name") else str(file)
    print("Uploaded file name:", file_name)
    summary = summarize_document(file)
    file_count += 1  # Increment count
    summary_audio = summary_text_to_speech(summary)
    # Enable voice chat after upload
    return (
        summary,
        gr.update(value=None, interactive=True),
        f"Files uploaded this session: {file_count}",
        file_count,
        summary_audio,
        gr.update(interactive=True),  # Enable mic_input
    )

def process_voice_input(transcribed_text):
    # Simulate sending the user's question to the AI backend and getting a response.
    # Replace this with your actual AI backend call.
    ai_response = f"{transcribed_text}"
    return ai_response

def tts_response(text):
    tts = gTTS(text=text, lang='en')
    audio_path = "ai_response.mp3"
    tts.save(audio_path)
    return audio_path

def transcribe_audio(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        try:
            user_text = recognizer.recognize_google(audio_data, language="en-US")
            return user_text
        except sr.UnknownValueError:
            return "[Unrecognized speech]"
        except sr.RequestError:
            return "[Speech recognition service unavailable]"

def handle_voice_chat(audio_file, chat_history):
    if audio_file is None:
        return chat_history, None, "\n".join([f"You: {u}\nAI: {a}" for u, a in zip(chat_history[::2], chat_history[1::2])]) if chat_history else ""
    user_text = transcribe_audio(audio_file)
    chat_history = chat_history or []
    chat_history.append(f"You: {user_text}")
    ai_text = process_voice_input(user_text)
    chat_history.append(f"AI: {ai_text}")
    ai_audio = tts_response(ai_text)
    conversation_display = "\n\n".join(chat_history)
    return chat_history, ai_audio, conversation_display

def export_conversation(chat_history):
    if not chat_history:
        return None
    conversation_text = "\n\n".join(chat_history)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as f:
        f.write(conversation_text)
        return f.name

# --- Gradio UI ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # 📄 Voice Reports
        **Upload a document to get a summary and enable voice chat!**
        """
    )

    # --- File Upload & Summary Block ---
    with gr.Group():
        gr.Markdown("## 📤 Document Upload & Summary")
        file_count_state = gr.State(0)
        with gr.Row():
            file_input = gr.File(
                label="Upload Document",
                interactive=True
            )
            summary_output = gr.Textbox(label="Summary", lines=10, interactive=False, show_copy_button=True)
        file_count_display = gr.Markdown("Files uploaded this session: 0")
        gr.Markdown("**Tip:** Uploading a new file will automatically replace the previous one.")
        with gr.Row():
            tts_audio = gr.Audio(label="Summary Audio", interactive=False, autoplay=True)

        file_input.upload(
            fn=handle_file_upload,
            inputs=[file_input, file_count_state],
            outputs=[
                summary_output,
                file_input,
                file_count_display,
                file_count_state,
                tts_audio,
                # mic_input will be enabled after upload
                # send_btn removed
            ]
        )

    # --- Voice Chat Block ---
    with gr.Group():
        gr.Markdown("## 🎤 Voice Chat")
        conversation_state = gr.State([])
        with gr.Row():
            mic_input = gr.Audio(
                sources=["microphone"],
                type="filepath",
                label="Speak Now",
                interactive=False  # Disabled until file upload
            )
            ai_audio = gr.Audio(label="AI Speaking", interactive=False, autoplay=True)
        chat_output = gr.Textbox(label="Conversation", lines=12, interactive=False, show_copy_button=True)
        with gr.Row():
            export_btn = gr.Button("Export Conversation")
            export_file = gr.File(label="Download Conversation")

        # Automatically process voice when recording stops
        mic_input.change(
            fn=handle_voice_chat,
            inputs=[mic_input, conversation_state],
            outputs=[conversation_state, ai_audio, chat_output]
        )

        export_btn.click(
            fn=export_conversation,
            inputs=[conversation_state],
            outputs=[export_file]
        )

    # Enable mic_input after file upload
    file_input.upload(
        fn=handle_file_upload,
        inputs=[file_input, file_count_state],
        outputs=[
            summary_output,
            file_input,
            file_count_display,
            file_count_state,
            tts_audio,
            mic_input  # Enable mic_input after upload
        ]
    )

demo.launch()
