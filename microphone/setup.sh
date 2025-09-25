#!/bin/bash

APP_NAME="conTabMic"
install_path="$(pwd)"   # default = current folder

# Prompt for desktop file
read -p "Create .desktop file? (y/n) " yn
case $yn in
 y|Y )
   DESKTOP_FILE="$APP_NAME.desktop"

   cat > "$DESKTOP_FILE" <<EOL
[Desktop Entry]
Name=$APP_NAME
Exec=$install_path/$APP_NAME
Icon=$install_path/icon.png
Type=Application
Categories=Utility;
Terminal=true
EOL

   mkdir -p ~/.local/share/applications
   mv "$DESKTOP_FILE" ~/.local/share/applications/
   chmod +x ~/.local/share/applications/$DESKTOP_FILE
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