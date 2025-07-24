#!/bin/bash
# Install script for Wind Waker Voice Chat controller permissions

echo "Wind Waker Voice Chat - Controller Permissions Setup"
echo "===================================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "This script needs sudo privileges to set up udev rules."
    echo "Please run: sudo $0"
    exit 1
fi

echo "Setting up uinput permissions..."

# Create udev rule for uinput access
echo "Creating udev rule at /etc/udev/rules.d/99-uinput.rules..."
cat > /etc/udev/rules.d/99-uinput.rules << EOF
# Allow access to uinput for Wind Waker Voice Chat controller support
KERNEL=="uinput", MODE="0666"
EOF

# Reload udev rules
echo "Reloading udev rules..."
udevadm control --reload-rules
udevadm trigger

# Load uinput module
echo "Loading uinput module..."
modprobe uinput

# Add uinput to modules to load at boot
echo "Adding uinput to /etc/modules-load.d/uinput.conf..."
echo "uinput" > /etc/modules-load.d/uinput.conf

echo ""
echo "✅ Setup complete!"
echo ""
echo "The uinput device is now accessible without sudo."
echo "This configuration will persist across reboots."
echo ""
echo "You can now run the controller daemon without sudo:"
echo "  cd waker && poetry run python controller_daemon.py"
