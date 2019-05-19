#!/bin/bash

# Run the script in /lib/voice_authen folder
g++ voice_authentication.cpp -shared -o /lib/x86_64-linux-gnu/security/pam_voice_authentication.so -fPIC
g++ train_users_voice.cpp -o /usr/bin/train_users_voice
