FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"
# For documentation/placeholder that the app expects this runtime env var
ENV GOOGLE_API_KEY=""

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
    xauth \
    xorg \
    libudev1 \
    tesseract-ocr \
    libx11-6 \
    libxext6 \
    libxrandr2 \
    libxinerama1 \
    libxfixes3 \
    # entr and git are removed as run_docker.sh is used
    curl \
    ca-certificates \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry system-wide
RUN curl -sSL https://install.python-poetry.org | python3 -

# Install RetroArch itself using Flatpak SYSTEM-WIDE
RUN flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
RUN flatpak install -y flathub org.libretro.RetroArch

# Create a non-root user - System will assign UID and GID
ARG USERNAME=smashuser
RUN groupadd $USERNAME \
    && useradd --gid $USERNAME -m -s /bin/bash $USERNAME \
    && usermod -aG video $USERNAME \
    && usermod -aG input $USERNAME

# Switch to the non-root user for subsequent commands
USER $USERNAME
WORKDIR /home/$USERNAME/app

# Create RetroArch cores directory (user-specific) and download/extract the N64 core
# This is done as the non-root user so it owns the files in its home directory
ENV RETROARCH_CORES_DIR="/home/$USERNAME/.var/app/org.libretro.RetroArch/config/retroarch/cores"
RUN mkdir -p ${RETROARCH_CORES_DIR} && \
    curl -SLfko /tmp/parallel_n64.zip https://buildbot.libretro.com/nightly/linux/x86_64/latest/parallel_n64_libretro.so.zip && \
    unzip -o /tmp/parallel_n64.zip -d ${RETROARCH_CORES_DIR}/ && \
    rm /tmp/parallel_n64.zip && \
    chmod +x ${RETROARCH_CORES_DIR}/parallel_n64_libretro.so

# Copy all application files from the (tar-prepared) build context
# The 'tar -h' command used in 'rebuild_and_run.sh' should ensure 'utils'
# is present as a real directory in the context passed to 'docker build -'.
# --chown will use the $USERNAME from the ARG defined earlier in the build stage,
# even though we're currently USER $USERNAME.
COPY --chown=$USERNAME:$USERNAME . .

# --- Temporary Debugging Lines (Remove after confirming 'utils' is copied correctly) ---
RUN echo "--- Listing /home/$USERNAME/app (user: $(whoami)) ---" && ls -la
RUN echo "--- Listing /home/$USERNAME/app/utils (user: $(whoami)) ---" && (ls -la utils || echo "'utils' directory not found or ls failed")
RUN if [ -f "utils/model.py" ]; then echo "utils/model.py found"; else echo "utils/model.py NOT found"; fi
RUN if [ -f "utils/params.py" ]; then echo "utils/params.py found (should NOT contain secrets)"; else echo "utils/params.py NOT found"; fi
# --- End Temporary Debugging Lines ---

# Configure poetry to create venv in project directory (as user)
RUN poetry config virtualenvs.in-project true

# Install Python dependencies (as user)
# This should now find utils if it was copied correctly
RUN poetry install --no-root --no-interaction --no-ansi --sync

# Create ROMs directory.
RUN mkdir -p /home/$USERNAME/var/roms
# IMPORTANT: Add your ROM file using ADD or mount as a volume during 'docker run'
# Example:
# ADD --chown=$USERNAME:$USERNAME SuperSmashBros.z64 /home/$USERNAME/var/roms/SuperSmashBros.z64
# Ensure the ROM filename in your virtual_controller.py matches this.

# Ensure entrypoint and run_docker scripts are executable
# COPY . . should preserve permissions if they are executable on the host.
# If not, uncomment these:
# RUN chmod +x entrypoint.sh
# RUN chmod +x run_docker.sh

ENV DISPLAY=:1
# ENTRYPOINT path uses the hardcoded username because $USERNAME (the ARG)
# is not expanded in the exec form of ENTRYPOINT.
ENTRYPOINT ["/home/smashuser/app/entrypoint.sh"]
