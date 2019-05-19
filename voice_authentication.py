# This is the heart of user voice authentication process. Once user records the voice, mfcc coefficients 
# are calculated and compared with mfcc coefficients of trained voice.
# Mounika Ponugoti, Apr 2017

#!/usr/bin/env python

from scipy.spatial import distance
from scipy.spatial.distance import euclidean
from pathlib import Path
from dtw import dtw

from helper import get_mfcc_coefficients
from helper import record_user_voice
from helper import ITERATIONS

import numpy as np
import wave, struct
import sys, os
import pyaudio
import pwd
import scipy.io.wavfile as wav

THRESHOLD = 27

np.set_printoptions(threshold=sys.maxsize)
	
def authenticate():
    # Temporary location to process
    rec_path = os.getenv("HOME") + "/rec"
    if not os.path.exists(rec_path):
        os.makedirs(rec_path)
    rec_filename = rec_path + "/" +"dst.wav"

    # Get the trained data corresponds to current user
    username = pwd.getpwuid(os.getuid())[0]
    path = "/lib/x86_64-linux-gnu/security/"
    source = path + username + "_source_mfcc_coefficients_"

    # To write the euclidean distance between trained and current sample
    dtw_filename = rec_path + "/" + "/dtw.txt"

    # If the file does not exist, create
    fd = os.open(dtw_filename, os.O_WRONLY + os.O_CREAT, 0o664)
    os.close(fd)
    dtw_outFile = open(dtw_filename, "w")

    record_user_voice(rec_filename)
    
    ''' To debug 
    print "rec_filename: " + rec_filename 
    print "dtw_filename: " + dtw_filename '''
    
    print ("Authenticating.... Please wait.....")
    current_mfcc_coeffi = get_mfcc_coefficients(rec_filename)
    
    at_least_one_exist = True
    
    for i in range(ITERATIONS):
        # Access each source file which has mfcc coefficients
        trained_source_filename = source + str(i) + ".txt"
        
        ''' To debug 
        print trained_source_filename '''
            
        is_exist = os.path.isfile(trained_source_filename)
        at_least_one_exist = at_least_one_exist and is_exist

        if not at_least_one_exist:
            exit("\nNo trained voice for " + username + " exist \nType 'sudo train_user_voice' to start training")

        if is_exist:
            trained_mfcc_file = Path(trained_source_filename)
            # Are coefficients valid?
            try:
                trained_mfcc_coeffi = np.loadtxt(trained_mfcc_file)
                dist, cost, acc, path = dtw(trained_mfcc_coeffi, current_mfcc_coeffi, euclidean)
            except:
                # If something wrong with training
                print ("\nVerify whether training is success or not")
                print ("If not, consider retraining")
                exit()
            
            # Write euclidean distance to file to access later
            dtw_outFile.write(str(dist))
            dtw_outFile.write(" ")

            if (dist <= THRESHOLD):
                break
	
    dtw_outFile.close()

if __name__ == '__main__':
    authenticate()
   
