"""
	Builds the Docs that need to be auto-generated for RMD.
"""
import sys
import os

dr = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../'))
print(dr)
sys.path.insert(0, dr)

from static import settings


# ================== Settings =========================================
tmpvars = {}
sl = './docs/Advanced_Usage/Settings_List.md'

default_override = {
	'user_agent': '[Unique ID]',
	'base_dir': '[Path to RMD Directory]'
}

sets = ''
seen = []
for item in settings.get_all():
	if not item.public:
		continue
	if item.category not in seen:
		seen.append(item.category)
		sets += '## %s\n' % item.category.title()
	if item.name in default_override:
		item.set(default_override[item.name])
	sets += '+ %s\n' % item.name
	sets += '    + **Description:** *%s* \n' % item.description
	sets += '    + **Expected Type:** %s \n' % item.type
	sets += '    + **Default value:** %s \n' % (item.val() if item.val() != '' else '[blank]')
	if item.opts:
		sets += '    + **Options:** \n'
		for o in item.opts:
			sets += '        + %s - *%s* \n' % o
tmpvars['settings_list'] = sets

with open(sl, 'r') as r:
	tmp = r.read()

with open(sl, 'w') as o:
	for k, v in tmpvars.items():
		tmp = tmp.replace('[%s]' % k, v)
	o.write(tmp)

print('+Built Docs Settings-List file!')
sys.exit(0)
