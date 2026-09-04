import streamlit as st
import yt_dlp
import tempfile
from pathlib import Path
import imageio_ffmpeg


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="YouTube Downloader",
    page_icon="⚡",
    layout="centered"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main {
    max-width: 850px;
    margin: auto;
}

.hero {
    padding: 35px 25px;
    border-radius: 22px;
    text-align: center;
    background: linear-gradient(135deg, #111827, #1f2937);
    margin-bottom: 30px;
}

.hero h1 {
    color: white;
    font-size: 42px;
    margin-bottom: 8px;
}

.hero p {
    color: #d1d5db;
    font-size: 17px;
}

.fast-box {
    padding: 15px;
    border-radius: 12px;
    background: #111827;
    text-align: center;
    margin-bottom: 20px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div class="hero">

<h1>⚡ YouTube Downloader</h1>

<p>
Ultra-fast video & audio downloader
</p>

</div>
""", unsafe_allow_html=True)


st.markdown("""
<div class="fast-box">

⚡ <b>High-Speed Download Engine</b><br>
Optimized concurrent downloading + FFmpeg

</div>
""", unsafe_allow_html=True)


# =========================================================
# URL INPUT
# =========================================================

url = st.text_input(
    "🔗 YouTube URL",
    placeholder="Paste YouTube video URL here..."
)


# =========================================================
# DOWNLOAD TYPE
# =========================================================

download_type = st.selectbox(
    "📁 Select Format",

    [
        "🎥 Best Video",
        "🎬 MP4 Video",
        "🎵 MP3 Audio"
    ]
)


# =========================================================
# DOWNLOAD BUTTON
# =========================================================

if st.button(
    "⚡ START FAST DOWNLOAD",
    type="primary",
    use_container_width=True
):

    # -----------------------------------------------------
    # URL CHECK
    # -----------------------------------------------------

    if not url.strip():

        st.warning("⚠️ Please enter a YouTube URL.")

        st.stop()


    # -----------------------------------------------------
    # TEMP DIRECTORY
    # -----------------------------------------------------

    output_folder = Path(
        tempfile.mkdtemp(
            prefix="fast_youtube_"
        )
    )


    # -----------------------------------------------------
    # FFMPEG
    # -----------------------------------------------------

    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()


    # =====================================================
    # FORMAT CONFIGURATION
    # =====================================================

    if download_type == "🎵 MP3 Audio":

        ydl_format = "bestaudio/best"

        postprocessors = [

            {
                "key": "FFmpegExtractAudio",

                "preferredcodec": "mp3",

                "preferredquality": "192"
            }

        ]


    elif download_type == "🎬 MP4 Video":

        ydl_format = (
            "bestvideo[ext=mp4]+bestaudio[ext=m4a]/"
            "best[ext=mp4]/best"
        )

        postprocessors = []


    else:

        ydl_format = (
            "bestvideo+bestaudio/best"
        )

        postprocessors = [

            {
                "key": "FFmpegVideoConvertor",

                "preferedformat": "mp4"
            }

        ]


    # =====================================================
    # PROGRESS DISPLAY
    # =====================================================

    progress_bar = st.progress(0)

    speed_text = st.empty()

    status_text = st.empty()


    # =====================================================
    # PROGRESS HOOK
    # =====================================================

    def progress_hook(data):

        if data["status"] == "downloading":

            downloaded = data.get(
                "downloaded_bytes",
                0
            )

            total = data.get(
                "total_bytes"
            ) or data.get(
                "total_bytes_estimate"
            )

            speed = data.get(
                "speed"
            )

            if total:

                percentage = int(
                    downloaded / total * 100
                )

                progress_bar.progress(
                    min(percentage, 100)
                )

            if speed:

                speed_mb = speed / (
                    1024 * 1024
                )

                speed_text.markdown(
                    f"### 🚀 Speed: `{speed_mb:.2f} MB/s`"
                )

            status_text.write(
                "⬇️ Downloading..."
            )

        elif data["status"] == "finished":

            progress_bar.progress(100)

            status_text.success(
                "✅ Download finished!"
            )


    # =====================================================
    # ULTRA FAST YT-DLP OPTIONS
    # =====================================================

    options = {

        # Format
        "format": ydl_format,


        # Output
        "outtmpl": str(
            output_folder /
            "%(title).100s.%(ext)s"
        ),


        # Don't download playlist
        "noplaylist": True,


        # -------------------------------------------------
        # SPEED OPTIMIZATION
        # -------------------------------------------------

        "concurrent_fragment_downloads": 16,

        "http_chunk_size": 10 * 1024 * 1024,

        "buffersize": 1024 * 1024,

        "retries": 3,

        "fragment_retries": 3,


        # -------------------------------------------------
        # Network optimization
        # -------------------------------------------------

        "socket_timeout": 30,

        "nocheckcertificate": True,


        # -------------------------------------------------
        # FFmpeg
        # -------------------------------------------------

        "ffmpeg_location": ffmpeg_path,


        # -------------------------------------------------
        # Post processing
        # -------------------------------------------------

        "postprocessors": postprocessors,


        # -------------------------------------------------
        # Progress
        # -------------------------------------------------

        "progress_hooks": [
            progress_hook
        ],


        # -------------------------------------------------
        # Quiet terminal output
        # -------------------------------------------------

        "quiet": True,

        "no_warnings": True,
    }


    # =====================================================
    # DOWNLOAD
    # =====================================================

    try:

        with st.spinner(
            "🔎 Connecting to YouTube..."
        ):

            with yt_dlp.YoutubeDL(
                options
            ) as ydl:

                info = ydl.extract_info(
                    url.strip(),
                    download=False
                )

                title = info.get(
                    "title",
                    "YouTube Video"
                )


        st.info(
            f"🎬 **{title}**"
        )


        # -------------------------------------------------
        # START DOWNLOAD
        # -------------------------------------------------

        with yt_dlp.YoutubeDL(
            options
        ) as ydl:

            ydl.download(
                [url.strip()]
            )


        # =================================================
        # FIND DOWNLOADED FILE
        # =================================================

        downloaded_files = [

            file

            for file in output_folder.iterdir()

            if file.is_file()

        ]


        if not downloaded_files:

            st.error(
                "❌ File was not created."
            )

            st.stop()


        file_path = max(

            downloaded_files,

            key=lambda file:
            file.stat().st_mtime

        )


        # =================================================
        # SUCCESS
        # =================================================

        st.success(
            "🎉 Download completed successfully!"
        )


        # =================================================
        # MIME TYPE
        # =================================================

        if file_path.suffix.lower() == ".mp3":

            mime_type = "audio/mpeg"

        else:

            mime_type = "video/mp4"


        # =================================================
        # DOWNLOAD BUTTON
        # =================================================

        st.download_button(

            label="⬇️ SAVE FILE",

            data=file_path.read_bytes(),

            file_name=file_path.name,

            mime=mime_type,

            use_container_width=True

        )


    # =====================================================
    # ERROR
    # =====================================================

    except Exception as error:

        st.error(
            "❌ Download failed."
        )

        st.code(
            str(error)
        )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "⚡ Powered by Streamlit • yt-dlp • FFmpeg"
)

st.caption(
    "Only download content you have permission or rights to download."
)