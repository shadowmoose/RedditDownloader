import os;
# WHen Travis installs everything, it will delete 'handlers/ytdl.py' and attempt to run the Updater.
# Make sure the updater worked.
def run_test(re):
	if not os.path.exists( os.path.join('handlers', 'ytdl.py') ):
		return 'YTDL Handler doesn\'t exist since it was deleted!',1;
	return '', 0;