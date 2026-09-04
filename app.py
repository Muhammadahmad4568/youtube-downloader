import streamlit as st
import yt_dlp
import tempfile
from pathlib import Path
import imageio_ffmpeg

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="YouTube Downloader",
    page_icon="⬇️",
    layout="centered"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
    .main {
        max-width: 850px;
        margin: auto;
    }

    .hero {
        padding: 35px 25px;
        border-radius: 20px;
        text-align: center;
        background: linear-gradient(135deg, #111827, #1f2937);
        margin-bottom: 30px;
    }

    .hero h1 {
        color: white;
        font-size: 40px;
        margin-bottom: 10px;
    }

    .hero p {
        color: #d1d5db;
        font-size: 17px;
    }

    .info-box {
        padding: 15px;
        border-radius: 12px;
        background: #1f2937;
        color: #d1d5db;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<div class="hero">
    <h1>⬇️ YouTube Downloader</h1>
    <p>Download videos or audio from a YouTube URL</p>
</div>
""", unsafe_allow_html=True)

# ---------------- INPUT ----------------
url = st.text_input(
    "🔗 YouTube URL",
    placeholder="Paste your YouTube URL here..."
)

# ---------------- FORMAT ----------------
download_type = st.selectbox(
    "📁 Select Download Type",
    [
        "🎥 Best Video",
        "🎬 MP4 Video",
        "🎵 MP3 Audio"
    ]
)

# ---------------- DOWNLOAD BUTTON ----------------
if st.button(
    "🚀 Download",
    type="primary",
    use_container_width=True
):

    if not url.strip():
        st.warning("⚠️ Please enter a YouTube URL.")
        st.stop()

    # Temporary folder
    output_folder = Path(
        tempfile.mkdtemp(prefix="youtube_download_")
    )

    # FFmpeg path
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

    # ---------------- FORMAT SETTINGS ----------------
    if download_type == "🎵 MP3 Audio":

        ydl_format = "bestaudio/best"

        postprocessors = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]

    elif download_type == "🎬 MP4 Video":

        ydl_format = "best[ext=mp4]/best"

        postprocessors = []

    else:

        ydl_format = "bestvideo+bestaudio/best"

        postprocessors = [
            {
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4"
            }
        ]

    # ---------------- YT-DLP OPTIONS ----------------
    options = {
        "format": ydl_format,

        "outtmpl": str(
            output_folder / "%(title).100s.%(ext)s"
        ),

        "noplaylist": True,

        "quiet": True,

        "no_warnings": True,

        "ffmpeg_location": ffmpeg_path,

        "postprocessors": postprocessors,
    }

    # ---------------- DOWNLOAD ----------------
    try:

        with st.status(
            "🔄 Processing...",
            expanded=True
        ) as status:

            with yt_dlp.YoutubeDL(options) as ydl:

                # Get video information
                info = ydl.extract_info(
                    url.strip(),
                    download=False
                )

                title = info.get(
                    "title",
                    "YouTube Video"
                )

                st.write(
                    f"🎬 **{title}**"
                )

                st.write(
                    "⬇️ Downloading..."
                )

                # Download
                ydl.download(
                    [url.strip()]
                )

            status.update(
                label="✅ Download completed!",
                state="complete"
            )

        # ---------------- FIND FILE ----------------
        downloaded_files = [
            file
            for file in output_folder.iterdir()
            if file.is_file()
        ]

        if not downloaded_files:

            st.error(
                "❌ Download completed but file was not found."
            )

            st.stop()

        file_path = max(
            downloaded_files,
            key=lambda file: file.stat().st_mtime
        )

        # ---------------- SUCCESS ----------------
        st.success(
            "🎉 Your file is ready!"
        )

        # ---------------- DOWNLOAD FILE ----------------
        if file_path.suffix.lower() == ".mp3":

            mime_type = "audio/mpeg"

        else:

            mime_type = "video/mp4"

        st.download_button(
            label="⬇️ Save File",
            data=file_path.read_bytes(),
            file_name=file_path.name,
            mime=mime_type,
            use_container_width=True
        )

    # ---------------- ERROR ----------------
    except Exception as error:

        st.error(
            "❌ Something went wrong."
        )

        st.code(
            str(error)
        )


# ---------------- FOOTER ----------------
st.divider()

st.markdown("""
<div class="info-box">
    💡 <b>Note:</b> Only download content that you have
    permission or rights to download and follow applicable
    platform and copyright rules.
</div>
""", unsafe_allow_html=True)

st.caption(
    "Built with Python • Streamlit • yt-dlp • FFmpeg"
)