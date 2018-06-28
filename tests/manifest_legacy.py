from classes.tools import manifest_converter as mc

# Make sure the Legacy Manifest Converter is still working with the test file.
# noinspection PyProtectedMember


def run_test(re):
	if mc._converted != 2:  # !cover
		return "Legacy Manifest did not fully convert: "+str(mc._converted), 1   # !cover
	return '', 0
