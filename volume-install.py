import os
import getpass

# Detect the path to the current script
current_script_path = os.path.abspath(__file__)

# Get the current user's home directory
user_home = os.path.expanduser("~")

# Set the path to your icon file
icon_path = os.path.join(user_home, "pyvolume", "volume.png")  # Assuming the icon is in the "pyvolume" folder

# Define the paths for the desktop entry and autostart script
desktop_entry_dir = os.path.join(user_home, ".config/autostart")
desktop_entry_path = os.path.join(desktop_entry_dir, "volume_control.desktop")

# Create the necessary directories if they don't exist
os.makedirs(desktop_entry_dir, exist_ok=True)

# Create a desktop entry file
desktop_entry = f"""[Desktop Entry]
Name=Volume Control
Exec=python3 {current_script_path}
Icon={icon_path}
Type=Application
StartupNotify=true
X-ICEWM-Taskbar-Icon=volume-control
"""

with open(desktop_entry_path, "w") as desktop_entry_file:
    desktop_entry_file.write(desktop_entry)

# Add an entry to IceWM autostart
autostart_script_path = os.path.join(user_home, ".icewm/autostart")

with open(autostart_script_path, "a") as autostart_script_file:
    autostart_script_file.write(f"/usr/bin/python3 {current_script_path} &\n")

# Restart IceWM (optional, you may need to log out and log back in)
os.system("pkill -x icewm")

print("Configuration completed. Your application will start at login with an icon in the taskbar.")
