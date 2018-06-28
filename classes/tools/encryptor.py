
"""  Basic encryption implementation. Should work cross-platform for any testing environment.  """

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import os
import sys


class Cryptor:
	def __init__(self):
		self.key_file = './settings_key.key'  # for dumping key during encryption.
		self.env_key = 'TRAVIS_RMD_TEST_FILE_KEY'
		self.key = self.load_key()

	def load_key(self):
		if self.env_key in os.environ:
			print('Key in env variable.')
			return base64.decodebytes(os.environ[self.env_key].strip().encode())
		if not os.path.exists(self.key_file):
			print('Generating new key.')
			return get_random_bytes(32)
		with open(self.key_file, 'r') as o:
			print('Loaded key from file.')
			return base64.decodebytes(o.read().encode())

	def encrypt(self, file, out_file="encrypted_test_settings.bin", save_key=True):
		with open(file, 'rb') as o:
			cipher = AES.new(self.key, AES.MODE_EAX)
			ciphertext, tag = cipher.encrypt_and_digest(o.read())

			file_out = open(out_file, "wb")
			[file_out.write(x) for x in (cipher.nonce, tag, ciphertext)]

			if save_key:
				with open(self.key_file, 'wb') as sf:
					sf.write(base64.encodebytes(self.key))

	def decrypt(self, file, file_out):
		# noinspection PyBroadException
		try:
			file_in = open(file, "rb")
			nonce, tag, ciphertext = [file_in.read(x) for x in (16, 16, -1)]
			cipher = AES.new(self.key, AES.MODE_EAX, nonce)
			data = cipher.decrypt_and_verify(ciphertext, tag)
			os.makedirs(os.path.dirname(file_out), exist_ok=True)
			with open(file_out, 'wb') as o:
				o.write(data)
		except Exception:
			print('Failed decryption.')
			sys.exit(1)


if __name__ == '__main__':
	if len(sys.argv) < 4:
		print('Invalid params. [encrypt/decrypt][file_in][file_out]')
		sys.exit(1)
	en = Cryptor()
	mode = sys.argv[1]
	f_in = sys.argv[2]
	f_out = sys.argv[3]
	if 'enc' in mode.lower():
		en.encrypt(f_in, f_out, True)
		print('Encrypted file [%s] into [%s]' % (f_in, f_out))
	else:
		en.decrypt(f_in, f_out)
		print('Decrypted file into: %s' % f_out)
