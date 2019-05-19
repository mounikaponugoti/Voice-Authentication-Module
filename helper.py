# Includes the helper functions 
# @Mounika Ponugoti, Apr 2017

from base import mfcc, delta
from audio_module import record
from audio_module import record_to_file

import numpy as np
import sys, pyaudio, os
import scipy.io.wavfile as wav
import time

ITERATIONS = 10

def get_mfcc_coefficients(src_file):
	''' Returns mfcc coefficients which are used later used for authentication 
	src_file: source file to read the recorded voice '''
	(rate,sig) = wav.read(src_file)
	mfcc_features = mfcc(sig,rate)
	delta_mfcc_features = delta(mfcc_features, 2)
	delta_delta_mfcc_features = delta(delta_mfcc_features, 2)
	mfcc_coefficients = np.concatenate((mfcc_features, delta_mfcc_features, delta_delta_mfcc_features), axis=1)
	return mfcc_coefficients
	

def delete_file(filename):
	''' Delete given file '''
	is_exist = os.path.isfile(filename)
	if is_exist:
	    os.remove(filename)
	return 0


def delete_dir(directory):
	''' Delete given directory '''
	if os.path.exists(directory):
	    os.rmdir(directory)	
	return 0
	

def delete_old_samples(path):
	''' If exist, deletes old files with mfcc coefficients'''
	for i in range(ITERATIONS):
		filename = path + str(i) + ".txt"
		my_file = os.path.isfile(filename)
		if my_file:
			os.remove(filename)
	return 0	

def move_old_samples(path, new_path):
	''' If exist, move old files with mfcc coefficients
	If there is an error while training, old samples are retrieved back '''
   
	for i in range(ITERATIONS):
		filename = path + str(i) + ".txt"
		new_filename = new_path + str(i) + ".txt"
		my_file = os.path.isfile(filename)
		if my_file:
			os.rename(filename, new_filename)
	return 0	
	
def record_user_voice(rec_filename):	
	''' Record user voice and write the samples to a file for later processing 
	rec_filename: name of the file to save samples '''
	
	print("Please read below sentence into the microphone \n")
	time.sleep(2)
	
	print("Hello, I am recognizer. Please identify yourself.\n")
	record_to_file(rec_filename)
	#rate,sig = record()
	
	print("End of recording\n")

	return 0
