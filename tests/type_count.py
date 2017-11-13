submissions = 4
comments = 1

# Checks how many, and which types, of posts/comments we've found.
def run_test(re):
	types_found = {}
	eles = re.get_elements()
	for e in eles:
		if e.type in types_found:
			types_found[e.type] = types_found[e.type]+1
		else:
			types_found[e.type] = 1
	# Check that we found the correct # of posts/comments.
	if types_found['Comment'] != comments or types_found['Submission'] != submissions:
		return 'Invalid posts or comment parsing: '+str(types_found) , 1
	return '', 0