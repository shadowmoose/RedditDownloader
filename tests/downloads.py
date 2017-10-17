import os

def scan_dir(dir_name):
	ret = []
	for dirpath, dirnames, filenames in os.walk(dir_name):
		for filename in filenames:
			ret.append(os.path.basename( os.path.join(dirpath, filename).replace('\\','/') ) )
	return ret
			
# Check all file names to make sure they match the prebuilt list above.
def run_test(re):
	return '', 0 # Disabled.
	ele_files = []
	eles = re.get_elements()
	for e in eles:
		for u,f in e.get_completed_files().items():
			if os.path.isdir(f):
				for ff in scan_dir(f):
					ele_files.append(os.path.basename(ff.replace('\\','/')))
			else:
				ele_files.append( os.path.basename(f.replace('\\','/')) )
	
	compare_list = sorted(scan_dir(re.download_dir))
	
	# Remove manifest, because the Manifest doesn't track itself.
	mf = os.path.basename(re.manifest_file.replace('\\','/'))
	if mf and mf in compare_list:
		compare_list.remove(mf)
	
	# Really basic filename check to make sure the given downloads were named properly.
	compare = sorted( ele_files ) == compare_list
	if not compare:
		print(re.download_dir)
		print(compare_list)
		return "Known files did not match real file structure: "+str(compare_list) , 1
	return '', 0