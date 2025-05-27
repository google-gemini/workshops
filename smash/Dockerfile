FROM ubuntu:latest

# This ARG will receive the filename of the tarball downloaded by rebuild_and_run.sh
ARG LIVEKIT_TARBALL_ARG

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-dev \
    python3-venv \
    python3-pip \
    build-essential \
    libudev-dev \
    flatpak \
    xvfb \
    libx11-6 \
    libxext6 \
    libxrandr2 \
    libxinerama1 \
    libxfixes3 \
    libxcursor1 \
    libxcomposite1 \
    libxdamage1 \
    ffmpeg \
    libx264-dev \
    libudev1 \
    tesseract-ocr \
    curl \
    ca-certificates \
    unzip \
    tar \
    x11-utils \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install LiveKit Server from the pre-downloaded tarball
COPY "${LIVEKIT_TARBALL_ARG}" /tmp/livekit.tar.gz
RUN echo "Installing LiveKit from /tmp/livekit.tar.gz (original filename was ${LIVEKIT_TARBALL_ARG})" && \
    # The livekit_X.Y.Z_linux_amd64.tar.gz from livekit/livekit contains 'livekit-server'
    tar -xzf /tmp/livekit.tar.gz -C /usr/local/bin/ livekit-server && \
    chmod +x /usr/local/bin/livekit-server && \
    rm /tmp/livekit.tar.gz \
    || (echo "Failed to install LiveKit server from copied tarball." && exit 1)

# Install Poetry system-wide
RUN curl -sSL https://install.python-poetry.org | python3 -

# Install RetroArch itself using Flatpak SYSTEM-WIDE
RUN flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
RUN flatpak install -y flathub org.libretro.RetroArch

# Create a non-root user
ARG USERNAME=smashuser
RUN groupadd $USERNAME \
    && useradd --gid $USERNAME -m -s /bin/bash $USERNAME \
    && usermod -aG video $USERNAME \
    && usermod -aG audio $USERNAME

USER $USERNAME
WORKDIR /home/$USERNAME/app

# Create RetroArch cores directory
ENV RETROARCH_CORES_DIR="/home/$USERNAME/.var/app/org.libretro.RetroArch/config/retroarch/cores"
RUN mkdir -p ${RETROARCH_CORES_DIR} && \
    curl -SLfko /tmp/parallel_n64.zip https://buildbot.libretro.com/nightly/linux/x86_64/latest/parallel_n64_libretro.so.zip && \
    unzip -o /tmp/parallel_n64.zip -d ${RETROARCH_CORES_DIR}/ && \
    rm /tmp/parallel_n64.zip && \
    chmod +x ${RETROARCH_CORES_DIR}/parallel_n64_libretro.so

# Copy all other application files from the (tar-prepared) build context
COPY --chown=$USERNAME:$USERNAME . .

# Configure poetry
RUN poetry config virtualenvs.in-project true

# Install Python dependencies
RUN poetry install --no-root --no-interaction --no-ansi --sync

# Create ROMs directory
RUN mkdir -p /home/$USERNAME/var/roms
# ADD --chown=$USERNAME:$USERNAME SuperSmashBros.z64 /home/$USERNAME/var/roms/SuperSmashBros.z64

ENV DISPLAY=:1
# entrypoint.sh should start livekit-server with --dev
ENTRYPOINT ["/home/smashuser/app/entrypoint.sh"]
