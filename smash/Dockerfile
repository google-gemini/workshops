# Stage 1: Build Poetry environment
FROM python:3.9-slim AS builder

# Install build tools and Python headers needed for C extensions
# THIS IS THE KEY FIX SECTION
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libudev-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install poetry
RUN pip install --no-cache-dir poetry

# Configure poetry to create venv in project directory for easier copying
RUN poetry config virtualenvs.in-project true

# Copy dependency definition files
COPY pyproject.toml poetry.lock ./

# Install Python dependencies (excluding development ones)
# The --sync option deprecation is a warning, not a fatal error for now.
# Added --without dev as it's good practice.
RUN poetry install --no-root --without dev --no-interaction --no-ansi --sync

# Stage 2: Main application image
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    flatpak \
    xvfb \
    xauth \
    xorg \
    libudev1 \
    tesseract-ocr \
    # Runtime libraries for mss (screenshots)
    libx11-6 \
    libxext6 \
    libxrandr2 \
    libxinerama1 \
    libxfixes3 \
    # For run.sh (entr & git ls-files). Consider simplifying run.sh for Docker.
    entr \
    git \
    # Utilities
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install RetroArch and N64 core using Flatpak SYSTEM-WIDE
RUN flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
RUN flatpak install -y flathub org.libretro.RetroArch
# Install Parallel N64 core (or Mupen64PlusNext if preferred)
RUN flatpak install -y flathub org.libretro.RetroArch.Core.ParallelN64
# Example: RUN flatpak install -y flathub org.libretro.RetroArch.Core.Mupen64PlusNext

# Create a non-root user
ARG USERNAME=smashuser
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    # Add user to video and input groups for potential hardware access
    && usermod -aG video $USERNAME \
    && usermod -aG input $USERNAME

USER $USERNAME
WORKDIR /home/$USERNAME/app

# Copy Python environment from builder stage
COPY --from=builder --chown=$USERNAME:$USERNAME /app/.venv /home/$USERNAME/app/.venv
# Add the venv to PATH
ENV PATH="/home/$USERNAME/app/.venv/bin:$PATH"

# Copy application code (ensure ownership by the non-root user)
COPY --chown=$USERNAME:$USERNAME . .

# Create ROMs directory.
RUN mkdir -p /home/$USERNAME/var/roms
# IMPORTANT: You need to ADD your ROM file here during build, or mount it as a volume.
# Make sure the ROM filename here matches what's in your virtual_controller.py script.
# Example:
# ADD --chown=$USERNAME:$USERNAME path/to/your/rom/Super\ Smash\ Bros.\ \(U\)\ \[!\].z64 /home/$USERNAME/var/roms/"Super Smash Bros. (U) [!].z64"

# Entrypoint script to start Xvfb and then the main application
COPY --chown=$USERNAME:$USERNAME entrypoint.sh /home/$USERNAME/app/entrypoint.sh
RUN chmod +x /home/$USERNAME/app/entrypoint.sh

ENV DISPLAY=:1

ENTRYPOINT ["/home/$USERNAME/app/entrypoint.sh"]
