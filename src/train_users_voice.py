# This is the actual file which enables the training user's voice and gets the  mfcc coffecients to use in future
# Mounika Ponugoti, Apr 2017

#!/usr/bin/env python
from helper import get_mfcc_coefficients
from helper import delete_old_samples
from helper import move_old_samples
from helper import record_user_voice
from helper import delete_file
from helper import delete_dir
from helper import ITERATIONS

import numpy as np
import sys, pyaudio, os

np.set_printoptions(threshold=sys.maxsize)

def train_user_voice():
    ''' 
    Collects features of user voice (mfcc coefficients) when user reads the sentence displayed on the screen.
    User voice is recorded for 10 times since it can't be 100% same every time 
    '''
    if os.geteuid() != 0:
        print("You require root privileges to change password.\nPlease try again using 'sudo train_users_voice'")
        exit()
		
    # Get username to seperate mfcc coefficients of multiple users
    username = os.getenv("SUDO_USER")
    path = "/lib/x86_64-linux-gnu/security/" + username + "_source_mfcc_coefficients_"
    new_path = "/lib/x86_64-linux-gnu/security/" + username + "_source_mfcc_coefficients_old" 
       
    # Keep old files aside to be safe
    move_old_samples(path, new_path)

    # Temporary directory to keep recordings
    rec_path = os.getenv("HOME") + "/rec"
    if not os.path.exists(rec_path):
	    os.makedirs(rec_path)
	
    filename_src = "source_"

    # Record user's voice multiple times
    for i in range(ITERATIONS):
        # Create seperate file for each recording
        print("\nCollecting sample "+ str(i) + "\n")
        coefficient_filename = path + str(i) + ".txt"
        rec_filename_src = rec_path + "/" + filename_src + str(i) + ".wav"

        # If the file does not exist, create
        fd = os.open(coefficient_filename, os.O_WRONLY | os.O_CREAT, 0o644)
        os.close(fd)
		
        '''To debug:
        print (rec_filename_src)
        print (coefficient_filename) '''

        # Record user voice and store to a .wav file for processing
        record_user_voice(rec_filename_src)

        # Get mfcc coefficients
        mfcc_outFile = open(coefficient_filename, 'w')
        mfcc_coefficients = get_mfcc_coefficients(rec_filename_src)
        np.savetxt(mfcc_outFile, mfcc_coefficients, fmt='%-7.8f')

        # Remove temporary file
        delete_file(rec_filename_src)
	    
    # Remove temporary directory
    delete_dir(rec_path)
    return 0

	
if __name__ == '__main__':
    username = os.getenv("SUDO_USER")
    path = "/lib/x86_64-linux-gnu/security/" + username + "_source_mfcc_coefficients_"
    new_path = "/lib/x86_64-linux-gnu/security/" + username + "_source_mfcc_coefficients_old" 
    try:
        train_user_voice()
        # If sucess, delete the old samples
        delete_old_samples(new_path)
    except:
        # If something is wrong, retrieve old files back
        move_old_samples(new_path, path)
