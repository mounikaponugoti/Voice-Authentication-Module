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

