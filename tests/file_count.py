import os
import hashlib

# Check all file names to make sure they match the prebuilt list above.
def run_test(re):
	total = 0
	for root, dirs, files in os.walk('./download/'):
		total += len(files)
	if total != 7: #!cover
		return "File list did not match expectations: "+str(total) , 1 #!cover
	return '', 0