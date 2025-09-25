#!/bin/bash
g++ -o controllerTab main.cpp -I/usr/include/SDL2 -lSDL2 -lSDL2_gfx -lSDL2_ttf -lX11 -lXtst
if [ $? -eq 0 ]; then
    x-terminal-emulator -e bash -c "stdbuf -o0 ./controllerTab; exec bash"
else
    x-terminal-emulator -e bash -c "echo Compilation failed.; echo Showing errors below:;
    echo; g++ -o controllerTab main.cpp -I/usr/include/SDL2 -lSDL2 -lSDL2_gfx -lSDL2_ttf -lX11 -lXtst 2>&1; exec bash"
fi
