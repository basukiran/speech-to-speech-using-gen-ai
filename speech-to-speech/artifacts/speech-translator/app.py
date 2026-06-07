import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import io

try:
    from googletrans import Translator
    GOOGLETRANS_AVAILABLE = True
except ImportError:
    GOOGLETRANS_AVAILABLE = False

# ─── Page Config ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Speech to Speech",
    page_icon="🎙️",
    layout="centered",
)

st.title("🎙️ Speech to Speech")
st.markdown(
    "Record your voice — get instant transcription, translation, and audio playback."
)
st.divider()

# ─── Language Selection ───────────────────────────────────────────────────────

direction = st.radio(
    "Translation Direction",
    options=["Kannada → English", "English → Kannada"],
    horizontal=True,
)

if direction == "Kannada → English":
    src_lang_code = "kn-IN"
    dest_lang_gtts = "en"
    dest_iso = "en"
    src_iso = "kn"
    src_label = "Kannada"
    dest_label = "English"
else:
    src_lang_code = "en-US"
    dest_lang_gtts = "kn"
    dest_iso = "kn"
    src_iso = "en"
    src_label = "English"
    dest_label = "Kannada"

st.divider()

# ─── Microphone Input ─────────────────────────────────────────────────────────

st.subheader(f"🎤 Record in {src_label}")
st.caption(
    f"Press the microphone button below, speak in {src_label}, then stop. "
    "When ready, click **Transcribe & Translate**."
)

audio_bytes = st.audio_input("Click the mic to start recording")

# ─── Process Button ───────────────────────────────────────────────────────────

st.divider()

process_btn = st.button(
    "🔄 Transcribe & Translate",
    type="primary",
    use_container_width=True,
    disabled=(audio_bytes is None),
)

if audio_bytes is None:
    st.info("📌 Record audio above, then click **Transcribe & Translate**.")

# ─── Processing Logic ─────────────────────────────────────────────────────────

if process_btn and audio_bytes is not None:

    # ── Step 1: Speech → Text ─────────────────────────────────────────────────
    with st.spinner(f"🔍 Recognising {src_label} speech…"):
        recognizer = sr.Recognizer()
        recognised_text = None
        try:
            audio_io = io.BytesIO(audio_bytes.read())
            with sr.AudioFile(audio_io) as source:
                audio_data = recognizer.record(source)
            recognised_text = recognizer.recognize_google(
                audio_data, language=src_lang_code
            )
        except sr.UnknownValueError:
            st.error(
                "❌ Could not understand the audio. "
                "Please speak clearly and try again."
            )
        except sr.RequestError as e:
            st.error(f"❌ Speech recognition service error: {e}")
        except Exception as e:
            st.error(f"❌ Unexpected error during recognition: {e}")

    if recognised_text:
        st.subheader(f"📝 Recognised {src_label} Text")
        st.success(recognised_text)

        # ── Step 2: Translate ─────────────────────────────────────────────────
        translated_text = None
        with st.spinner("🌐 Translating…"):
            try:
                if not GOOGLETRANS_AVAILABLE:
                    raise RuntimeError("googletrans is not installed")
                translator = Translator()
                result = translator.translate(
                    recognised_text, src=src_iso, dest=dest_iso
                )
                translated_text = result.text
            except Exception as e:
                st.error(f"❌ Translation error: {e}")

        if translated_text:
            st.subheader(f"🌏 Translated {dest_label} Text")
            st.success(translated_text)

            # ── Step 3: Text → Speech ─────────────────────────────────────────
            with st.spinner("🔊 Generating audio…"):
                try:
                    tts = gTTS(text=translated_text, lang=dest_lang_gtts)
                    tts_buf = io.BytesIO()
                    tts.write_to_fp(tts_buf)
                    tts_buf.seek(0)

                    st.subheader("🔊 Translated Audio")
                    st.audio(tts_buf, format="audio/mp3", autoplay=True)
                except Exception as e:
                    st.error(f"❌ Text-to-speech error: {e}")

# ─── Footer ───────────────────────────────────────────────────────────────────

st.divider()
st.caption(
    "Powered by Google Speech Recognition • Google Translate • gTTS"
)
