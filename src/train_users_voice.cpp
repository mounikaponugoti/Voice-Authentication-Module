// This is a wraper to train the user voice
// Mounika Ponugoti, Apr 2017

#include <stdlib.h>
#include <stdio.h>

int main() {
    system("python /lib/voice_authen/train_users_voice.py 2> /dev/null");
   // Comment above line and uncomment below line if you want to see warnings printed on the standard output
   // system("python /lib/voice_authen/train_users_voice.py");
   return 0;
}
