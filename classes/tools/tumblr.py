import requests

def get_page(url):

	# remove embed
	if "/embed" in url:
		url = url[:-6]

	# remove safe-mode
	if "safe-mode?url=" in url:
		url = url.split("safe-mode?url=")[1]

	# make url
	url = url.split("#")[0]
	url = url.split("?")[0]
	url += "/xml"

	# get page
	request = requests.get(url, allow_redirects=False)
	loc = request.headers.get("location")

	# if redirect, get page using new url
	if loc is not None:
		url = loc
		url = url.split("#")[0]
		url = url.split("?")[0]
		url += "/xml"
		print('new url:', url)
		request = requests.get(url, allow_redirects=False)
	print('loc: ', loc)
	print(url)
	print(request.status_code, request.url)
	return request.text

print(get_page(input('URL: ').strip()))
