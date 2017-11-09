import os
import hashlib
# Stores filenames as SHA1 hashes.
compare_list = ['4495787b8c32690b5e8c909790733b3c7a54a14e', '4495787b8c32690b5e8c909790733b3c7a54a14e', 'a44e73ff85faf9ca869ab289fa16daf3b3de74e7', 'b68b40b64a5d75c4b80ef15e24f71f2ad6bbe3a3', 'cd1e6bf8a5c5fbebf9ec08fe801aab983520f961'];
compare_list.sort()

# Check all file names to make sure they match the prebuilt list above.
def run_test(re):
	files = []
	eles = re.get_elements()
	for e in eles:
		for u,f in e._file_map.items():
			files.append( os.path.basename(str(f).replace('\\','/')) )
	#print(sorted( [hashlib.sha1(s.encode('utf-8')).hexdigest() for s in files] ));
	
	# Really basic filename check to make sure the given downloads were named properly.
	compare = sorted( [hashlib.sha1(s.encode('utf-8')).hexdigest() for s in files] ) == compare_list
	if not compare:
		return "File list did not match expectations: "+str(sorted(files)) , 1
	return '', 0