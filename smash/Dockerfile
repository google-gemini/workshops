FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install system dependencies including Python, build tools, and runtime needs
# This will use the default python3, python3-dev, etc. from ubuntu:latest
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Python (default for the Ubuntu base) and related tools
    python3 \
    python3-dev \
    python3-venv \
    python3-pip \
    # Build tools for C extensions (like python-uinput)
    build-essential \
    libudev-dev \
    # Flatpak and X environment
    flatpak \
    xvfb \
    xauth \
    xorg \
    # Runtime for uinput
    libudev1 \
    # Tesseract
    tesseract-ocr \
    # Runtime libraries for mss (screenshots)
    libx11-6 \
    libxext6 \
    libxrandr2 \
    libxinerama1 \
    libxfixes3 \
    # For run.sh (if still used as is) - consider simplifying run.sh
    entr \
    git \
    # Utilities
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry system-wide (using the system's default python3)
RUN curl -sSL https://install.python-poetry.org | python3 -

# Install RetroArch and N64 core using Flatpak SYSTEM-WIDE
RUN flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
RUN flatpak install -y flathub org.libretro.RetroArch
RUN flatpak install -y flathub org.libretro.RetroArch.Core.ParallelN64
# Example: RUN flatpak install -y flathub org.libretro.RetroArch.Core.Mupen64PlusNext

# Create a non-root user
ARG USERNAME=smashuser
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && usermod -aG video $USERNAME \
    && usermod -aG input $USERNAME

USER $USERNAME
WORKDIR /home/$USERNAME/app

# Configure poetry to create venv in project directory (as user)
RUN poetry config virtualenvs.in-project true

# Copy dependency definition files
COPY --chown=$USERNAME:$USERNAME pyproject.toml poetry.lock ./

# Install Python dependencies (as user)
# Poetry will use the Python version active in the PATH, which should be the system's default python3
RUN poetry install --no-root --no-interaction --no-ansi --sync

# Copy application code (ensure ownership by the non-root user)
COPY --chown=$USERNAME:$USERNAME . .

# Create ROMs directory.
RUN mkdir -p /home/$USERNAME/var/roms
# IMPORTANT: You need to ADD your ROM file here during build, or mount it as a volume.
# Example:
# ADD --chown=$USERNAME:$USERNAME path/to/your/rom/Super\ Smash\ Bros.\ \(U\)\ \[!\].z64 /home/$USERNAME/var/roms/"Super Smash Bros. (U) [!].z64"

# Entrypoint script to start Xvfb and then the main application
COPY --chown=$USERNAME:$USERNAME entrypoint.sh /home/$USERNAME/app/entrypoint.sh
RUN chmod +x /home/$USERNAME/app/entrypoint.sh

ENV DISPLAY=:1

ENTRYPOINT ["/home/$USERNAME/app/entrypoint.sh"]
