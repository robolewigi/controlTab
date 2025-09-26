#!/bin/bash

APP_NAME="microphoneConTab"
install_path="$(pwd)"   # default = current folder

# Prompt for desktop file
read -p "Create .desktop file and dependencies (y/n) " yn
case $yn in
 y|Y )
   DESKTOP_FILE="$APP_NAME.desktop"

   sudo apt update
   sudo apt install -y libasound2 libportaudio2 libportaudiocpp0 \
    ffmpeg libnss3 libx11-6 libxtst6 libxrender1 libxext6 \
    libglib2.0-0 libudev1 alsa-utils unzip wget

   # Ask user which terminal to use
   read -p "Enter terminal to use [gnome-terminal]: " user_terminal
   TERMINAL=${user_terminal:-gnome-terminal}

   # Decide Exec line based on terminal
   case $TERMINAL in
     gnome-terminal)
       EXEC_LINE="$TERMINAL -- bash -c '$install_path/conTabMic; exec bash'"
       ;;
     konsole)
       EXEC_LINE="$TERMINAL -e bash -c '$install_path/conTabMic; exec bash'"
       ;;
     xfce4-terminal)
       EXEC_LINE="$TERMINAL --command=\"bash -c '$install_path/conTabMic; exec bash'\""
       ;;
     *)
       # Default fallback
       EXEC_LINE="$TERMINAL -- bash -c '$install_path/conTabMic; exec bash'"
       ;;
   esac

   cat > "$DESKTOP_FILE" <<EOL
[Desktop Entry]
Name=$APP_NAME
Exec=$EXEC_LINE
Icon=$install_path/icon.png
Type=Application
Categories=Utility;
Terminal=false
EOL

   mkdir -p ~/.local/share/applications
   mv "$DESKTOP_FILE" ~/.local/share/applications/
   chmod +x ~/.local/share/applications/$DESKTOP_FILE
   echo "Desktop file created at ~/.local/share/applications/$DESKTOP_FILE"
   ;;
 * )
   echo "Skipping desktop file."
   ;;
esac

read -p "Download vosk-model-en-us-0.22-lgraph at $(pwd) (y/n) " yn
case $yn in
 y|Y )
   cd "$(pwd)" || exit 1
   if wget -c https://alphacephei.com/vosk/models/vosk-model-en-us-0.22-lgraph.zip; then
     unzip -o vosk-model-en-us-0.22-lgraph.zip
     echo "worked"
   else
     echo "error"
   fi
   ;;
 * )
   echo "Skipping model download."
   ;;
esac

echo "done"
read