# Voice-Authentication-Module 

PAM (pluggable authentication module) provides common authentication scheme for variety of applications and services.
This provides the flexibility and control over the authentication of the applications and services. The authentication modules 
are attached dynamically at run-time. In order to use PAM, an application requires to have a file in `/etc/pam.d`

The format of each rule in the file in `/etc/pam.d/` is 
```
module_interface    control_flag     module_name     module_arguments
```
* *module_interface* can be any of the following:
  * **Auth:** Authenticates the user and verifies the validity of the password
  * **Account:** Checks whether the account is valid in the current conditions e.g. check whether access is allowed, account expiry, time-based login.
  * **Password:** Responsible for updating the passwords. With this interface, rules for the passwords can be enforced
  * **Session:** Allocates the resources that user might need during login sessions or cleanup of a service for a user 
e.g. mounting user’s home directory, setting resource usage limits, printing a message of the day

* *control_flag* define the expected behavior of that module and it can be any of the following:
  * **Required:** Module must pass to result success
  * **Requisite:** Module must pass otherwise no further modules are run
  * **Sufficient:** If the module is pass no further modules in the stack are called, otherwise ignored
  * **Optional:** The result of this module is used only if this is the only module in the stack for this service

* *module_name* defines what module to invoke for the authentication e.g. one can add voice authentication or face authentication or typing speed to authenticate user
* *module_arguments* defines the arguments to be supplied to the module if required

* *@include* fetches all the lines from the specified file.
 
## Sample Example
```
$ cat /etc/pam.d/su

auth       sufficient pam_rootok.so
session    required   pam_env.so readenv=1
session    required   pam_env.so readenv=1 envfile=/etc/default/locale
session    optional   pam_mail.so nopen
session    required   pam_limits.so
@include common-auth
@include common-account
@include common-session
```

## Goal
The main goal of this project is to provide voice based authentication module for Linux based systems for `sudo` access.

## Dependencies
python, numpy, scipy, pyaudio, pyaudio needs ALSA library, libasound2-dev, libpam0g-dev, pathlib

## Source files 	
* audio_module.py - detects and records the audio
* base.py - mfcc and delta coefficients calculation
* dtw.py - dynamic time warping algorithm implementation
* helper.py - common functions
* sigproc.py - divides the signal into frames 
* train_users_voice.cpp - wrapper for python file train_users_voice.py 
* train_users_voice.py -  actual training module
* voice_authentication.cpp - wrapper for python file voice_authentication.py
* voice_authentication.py - actual authentication implementation

## Installation
```
sudo mkdir /lib/voice_authen
cd /lib/voice_authen
./script.sh   (This will create the voice trainer and pam_voice_authentication module)
```

Edit the PAM configuration file in `/etc/pam.d/sudo` and add the following line to enable voice authentication for `sudo` service
```
auth   sufficient   pam_voice_authentication.so
```

### Configuration file after modification
```
$ cat /etc/pam.d/sudo

#%PAM-1.0

session  required   pam_env.so readenv=1 user_readenv=0
session  required   pam_env.so readenv=1 envfile=/etc/default/locale user_readenv=0
auth    sufficient pam_voice_authentication.so 

@include common-auth
@include common-account
@include common-session-noninteractive
```
Voice authentication module can also be added to other services like su, ssh, login etc. 
However, it requires to edit the corresonding configuration files. Before you change any configuration get familiar with the terms and usage.

## Usage 
Once the voice authentication module is configured, user who has root privileges can train their voice. Trained voice is analyzed and required information is stored in a file. When the user uses `sudo` service, user is asked to read a given sentence into the microphone. Since human voice is hard to reproduce, training module records multiple samples for reference. While authenticating, recorded voice is compared with all the trained samples. If any of the samples matches, access is granted. Verification process is time consuming. This can be speedup with multi-threaded program on CPU or by using GPGPU. However, that's not the main goal of this project.

*	To train/change the existing voice run the command `sudo train_users_voice`
* To test the module type a dummy command `sudo apt-get install abc`

### Training process
1.	User is asked to read a sentence prompted on the screen into the microphone.
2.	Recorded voice is stored in a temporary directory and trimmed if there is silence in the beginning and in the end. This is done by dropping the samples which have amplitude less than the given threshold [4]. The samples of the recorded voice from wav file is read and stored in an array.
3.	39 MFCC coefficients (12 MFCC+1 energy+12 delta+1 energy of delta+ 12 delta-delta+ 1 energy of delta delta) are calculated by using the library written in python [5]. The MFCC coefficients are stored in a file for future reference.
4. Since voice may not be identical everytime, 10 training samples are collected. However, the number of training samples can be changed by modifying the iterations variable in appropriate files.
5. Once all the samples are collected, training process is terminated.

### Authentication process
1.	The authentication process follows same steps as in training process to record and calculate the MFCC coefficients.
4.	DTW algorithm [3,6] available here [1] is used to compare the 39 MFCC coefficients of each trained sample voice against the 39 MFCC coefficients of recorded voice for authentication. DTW returns the cost matrix, path, accumulated cost, and minimum distance. Minimum distance for each trained sample is written to a file to access it later.
5.	In a C++ program where python code is invoked, the results of DTW algorithm are read. If the mininum distance of any trained sample is less than the threshold, access is granted. If the access is denied, it asks the user to enter regular password to authenticate.

## Other available libraries
There are some existing DSP libraries that can be used to calculate MFCC, DTW, FFT, spectrum of a signal, and frequency of a signal in C++ and python. Kaldi, HTK, Aubio, Aquila, Praat are some of the existing C++ libraries. However, while experimenting with these libraries, I faced following problems:
*	Kaldi and HTK support many features but I could not understand how to interface.
*	Aubio is small and easily understandable library but it does not support DTW algorithm.
*	Aquila is a good library but while calculating MFCC coefficients with recorded signal, it gave some errors on deleting pointers.

## Test Environment
This module has been verified on a VMware virtual machine. Guest system runs Ubuntu_16.04_64bit LTS on windows 10 host.

## Know Issues
* Make sure you have a recording driver on windows host and sound card is connected to the virtual machine if you are using.
* Use proper microphone.

## Limitations
* Currently, this module uses only 39 MFCC coefficients as a feature of voice.
* While training this module does not verify whether the user is actually talking or not.

## Things can be improved
*	This module uses MFCC coefficients for authentication. Instead, pitch of a human voice can also be extracted and combined with MFCC coefficients as discussed in [7]. In addition, one can also extract and use other features like intensity of the voice, spectrum of the signal, frequency range of the voice etc.
*	To recognize the pattern, other than DTW algorithm such as Hidden Markov Models (HMM) or Gaussian Mixture Model (GMM) can be used.
*	Instead of relaying on same text for training and verification, one can ask the user to talk or read anything. However, this requires to extract features from the user voice which are independent of what the user read or talk. This is usually used in speaker recognition [2]. 
* Machine learning algorithms may yield better results by learning continuously.

## References
1.	Pierre Rouanet. 2017. dtw: DTW (Dynamic Time Warping) python module. Retrieved June 23, 2017 from https://github.com/pierre-rouanet/dtw
2.	Speaker recognition. Wikipedia. Retrieved June 23, 2017 from https://en.wikipedia.org/w/index.php?title=Speaker_recognition&oldid=763719322
3.	Dynamic time warping. Wikipedia. Retrieved June 23, 2017 from https://en.wikipedia.org/w/index.php?title=Dynamic_time_warping&oldid=778818008
4.	wav - Detect & Record Audio in Python - Stack Overflow. Retrieved June 23, 2017 from https://stackoverflow.com/questions/892199/detect-record-audio-in-python
5.	Practical Cryptography. Retrieved June 23, 2017 from http://practicalcryptography.com/miscellaneous/machine-learning/guide-mel-frequency-cepstral-coefficients-mfccs/
6.	Microsoft Word - 138-143 - 1003.4083.pdf. Retrieved June 23, 2017 from https://arxiv.org/ftp/arxiv/papers/1003/1003.4083.pdf
7.	odyssey - odyssey2001EzzaidiRouat.pdf. Retrieved June 23, 2017 from http://www.gel.usherbrooke.ca/rouat/publications/odyssey2001EzzaidiRouat.pdf

## Useful resources:
1.	https://www.linux.com/news/understanding-pam
2.	https://stackoverflow.com/questions/892199/detect-record-audio-in-python
3.	https://stackoverflow.com/questions/7078226/comparing-audio-recordings
4.	https://dsp.stackexchange.com/questions/8342/how-to-stitch-together-mfccs-from-multiple-frames
5.	https://stackoverflow.com/questions/27891629/comparing-two-recorded-voices
6.	https://dsp.stackexchange.com/questions/17300/in-framing-of-audio-samples-what-is-need-of-frame-shift-while-giving-frame-siz
7.	https://dsp.stackexchange.com/questions/7581/speech-comparison-algorithm-for-rating-on-similarities
8.	https://github.com/beatgammit/simple-pam/blob/master/src/mypam.c
9.	https://www.howtoforge.com/tutorial/how-to-configure-sudo-for-two-factor-authentication-using-pam-radius-on-ubuntu-and-centos/
10.	http://www.tuxradar.com/content/how-pam-works
11.	http://www.rkeene.org/projects/info/wiki/222


