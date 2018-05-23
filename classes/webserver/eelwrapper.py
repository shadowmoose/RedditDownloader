import eel
import sys
import os


_file_dir = None
_web_dir = None

"""
	Eel is great, but doesn't expose everything we want.
	So by locking Eel to specific versions, we can easily override whatever we need here.
	
	See simple documentation: https://bottlepy.org/docs/dev/tutorial.html
"""

def start(web_dir, file_dir):
	global _file_dir, _web_dir
	_file_dir = os.path.abspath(file_dir)
	_web_dir = os.path.abspath(web_dir)

	eel.init(web_dir)
	eel.start('index.html', block=False)
	print('Started WebUI!')


def _websocket_close():
	# a websocket just closed
	# TODO: user definable behavior here
	print('Websocket closed.')
	eel.sleep(1.0)
	if len(eel._websockets) == 0:
		print('Out of websockets. Terminating...')
		sys.exit()


@eel.btl.route('/file')
def _downloaded_files():
	""" Allows the UI to request files RMD has scraped.
		In format: "./file?id=Path/to/File.jpg"
	"""
	file_path = eel.btl.request.query.id
	print(f'Requested RMD File: {file_path}')
	return eel.btl.static_file(file_path, root=_file_dir)


eel._websocket_close = _websocket_close





if __name__ == '__main__':
	start('../../web/', '../../../download')
	while True:
		eel.sleep(2)
