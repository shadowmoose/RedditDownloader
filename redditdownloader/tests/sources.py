import sources

# Tests loading Source objects, not their posts.

source_list = [{
	"alias": "default",
	"data": {
		'owner': '',
		'multi_name': '',
		'order': 'top',
		'time': 'all',
		'limit': 0
	},
	"filters": {
		"created_utc.max": 0,
		"score.min": 1000,
		"title.match": "re"
	},
	"type": "multi-reddit-source"
}]


def run_test(re):
	sl = sources.load_sources()
	for s in sl:
		if not s.get_alias():
			return 'Missing Source alias! (%s)' % s, 1
		if 'test' in s.get_alias():
			return 'Loaded test Source by mistake.', 2

	sl = sources.load_sources(source_list)
	if len(sl) != len(source_list):
		return 'Error loading test source list!', 1
	for s in sl:
		# print(s)
		if 'multi' not in s.type:
			return 'Loaded source is of invalid type!', 2
		if s.to_obj() != source_list[0]:
			print(s.to_obj())
			return 'Converted Source does not match original!', 3
	return '', 0
