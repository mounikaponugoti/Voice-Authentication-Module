// PAM voice authentication module 
// Mounika Ponugoti, Apr 2017

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <security/pam_appl.h>
#include <security/pam_modules.h>
#include <unistd.h>
#include <sys/types.h>
#include <pwd.h>

#define THRESHOLD 27
#define ITERATIONS 10

/* expected hook */
PAM_EXTERN int pam_sm_setcred(pam_handle_t *pamh, int flags, int argc, const char **argv ) {
	return PAM_SUCCESS;
}

PAM_EXTERN int pam_sm_acct_mgmt(pam_handle_t *pamh, int flags, int argc, const char **argv) {
	printf("Acct mgmt\n");
	return PAM_SUCCESS;
}

/* expected hook, this is where custom stuff happens */
PAM_EXTERN int pam_sm_authenticate( pam_handle_t *pamh, int flags,int argc, const char **argv ) {
	double dist = 100, minValue = 1000;
	FILE *inp;
	int errno, ret_val;
	
	ret_val = system("python /lib/voice_authen/voice_authentication.py 2> /dev/null ");
	// Comment above line and uncomment below line if you want to see warnings printed on the standard output
	// ret_val = system("python /lib/voice_authen/voice_authentication.py ");

	if (!(ret_val == 0 && errno == 0))
		perror("There was an error");

	char file[256]; 

	// Result of python (minimum distance) is written to a file. Now opening here to read it.
	strcat(strcpy(file, getenv("HOME")), "/rec/dtw.txt");
	inp = fopen(file,"r");

    // Is file opened?
	if (inp == NULL) {
		perror("Failed to open: ");
		return PAM_PERM_DENIED;
	}

	for(int i = 0; i < ITERATIONS; i++){
		fscanf(inp, "%lf", &dist);
		if(minValue > dist){
			minValue = dist;
			if(minValue <= THRESHOLD)
				break;
		}
	}
	
	if (minValue <= THRESHOLD){
		printf("You are authenticated.\n");
		// Delete temporary directory
		system("rm -rf $HOME/rec 2> /dev/null");
		return PAM_SUCCESS;
	}

	else { 
		printf("\nFailed to authenticate \nPlease try again later!!\n\n");
		// Delete temporary directory
		system("rm -rf $HOME/rec 2> /dev/null");
		return PAM_PERM_DENIED;
	}
}

    

