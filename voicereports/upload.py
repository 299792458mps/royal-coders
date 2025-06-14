import gradio as gr
import speech_recognition as sr
import os
from gtts import gTTS

def summarize_document(file):
    return "This is a placeholder summary. Replace this with actual summary logic."

def process_voice_input(transcribed_text):
    return f"Processed response to: {transcribed_text}"

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
    # Generate TTS audio for the summary
    summary_audio = summary_text_to_speech(summary)
    # Clear file input after upload
    return summary, gr.update(value=None, interactive=True), f"Files uploaded this session: {file_count}", file_count, summary_audio

def handle_audio_input(audio_file):
    if audio_file is None:
        return "No audio input provided."
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language="en-US")
            return process_voice_input(text)
        except sr.UnknownValueError:
            return "Sorry, could not understand the audio."
        except sr.RequestError:
            return "Speech recognition service is unavailable."

def clear_audio():
    # This will clear the audio input and the chat output
    return gr.update(value=None), gr.update(value="")

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # 📄 Voice Reports
        **Upload a document to get a summary and enable voice chat!**
        <br>
        <span style='color:gray'>Step 1: Upload your document.<br>
        Step 2: Review the summary.<br>
        Step 3: Use your microphone to ask questions about the document.</span>
        """,
        elem_id="main-title"
    )

    file_count_state = gr.State(0)  # Session state for file count

    with gr.Accordion("📤 Document Upload & Summary", open=True):
        with gr.Row():
            file_input = gr.File(
                label="Upload Document",
                interactive=True
            )
            summary_output = gr.Textbox(label="Summary", lines=10, interactive=False, show_copy_button=True)
        file_count_display = gr.Markdown("Files uploaded this session: 0")
        gr.Markdown("**Tip:** Uploading a new file will automatically replace the previous one.")

        with gr.Row():
            # Removed the Speak Summary button
            tts_audio = gr.Audio(label="Summary Audio", interactive=False, autoplay=True)

    with gr.Accordion("🎤 Voice Chat", open=True):
        with gr.Row():
            mic_input = gr.Audio(
                sources=["microphone"],
                type="filepath",
                label="Speak Now",
                interactive=True
            )
            chat_output = gr.Textbox(label="Response", lines=4, interactive=False, show_copy_button=True)
        retry_btn = gr.Button("Retry")

    file_input.upload(
        fn=handle_file_upload,
        inputs=[file_input, file_count_state],
        outputs=[summary_output, mic_input, file_count_display, file_count_state, tts_audio]
    )
    mic_input.change(fn=handle_audio_input, inputs=mic_input, outputs=chat_output)
    retry_btn.click(fn=clear_audio, outputs=[mic_input, chat_output])

demo.launch()
