"""
	The main setup Wizard.
"""
import stringutil as su
from colorama import Fore
import webbrowser
import praw
import prawcore
import sys
from settings import Settings
import console
import wizards.source_wizard as source_wizard
import wizards.wizard_functions as wizard_functions

def run(settings_file='settings.json'):
	client_setup = {'secret':None, 'id':None}
	user_setup = {'username':None, 'password':None}

	su.print_color(Fore.GREEN, "Welcome to the Reddit Media Downloader automatic setup!")
	su.print_color(Fore.YELLOW, '\tThis program will help you automatically set everything up in a few steps.')

	su.print_color(Fore.CYAN, "To start, we need to register this script with reddit.")
	su.print_color(Fore.CYAN, "I'll walk you through this, & the visual guide can be found here: https://goo.gl/ox6PmA")
	su.print_color(Fore.YELLOW, "\tReddit requires that any program accessing it is registered.")
	su.print_color(Fore.YELLOW, "\tFor your account's security, you need to do this yourself.")

	su.print_color(Fore.CYAN, "Open https://www.reddit.com/prefs/apps, and sign in.")
	if console.confirm('\tIs it okay to open the URL in your browser for you?'):
		webbrowser.open('https://www.reddit.com/prefs/apps')

	su.print_color(Fore.CYAN, "Once you're signed in, scroll down and click on 'Create Application'.")
	print()
	su.print_color(Fore.CYAN, "Give it a name to remind you what it's for in the future, and select the 'Script' option.\n")
	su.print_color(Fore.YELLOW, "The description can be anything to remind yourself.")
	su.print_color(Fore.YELLOW, "The URL and URI fields don't matter, so they can be set to 'http://localhost', or a made-up URL.")
	print('\n')
	su.print_color(Fore.YELLOW, "Go ahead and click 'Create App' after you've filled this all in, then press Enter here.")
	console.pause()

	su.print_color(Fore.CYAN, "Now that you've registered your script, scroll to it on the page and get its ID (the random text under 'personal use script' on top of its box)")
	su.print_color(Fore.YELLOW, "\t(This is your client_id)")
	client_setup['id'] = console.string("Paste or type your client ID here")

	su.print_color(Fore.CYAN, "\nAlso grab the generated 'Secret'.")
	su.print_color(Fore.YELLOW, "\t(This is your client_secret)")
	client_setup['secret'] = console.string("Paste or type your client Secret here")

	su.print_color(Fore.GREEN, "Excellent!\nNow, finally, this script will need the username and password of the account that registered this script.")
	su.print_color(Fore.GREEN, "\tYour credentials will be stored locally, and never sent anywhere - don't worry;")
	su.print_color(Fore.GREEN, "\tThe whole point of the last few steps was to keep your information safe!")

	user_setup['username'] = console.string('Enter your username')
	user_setup['password'] = console.string('Enter your password')
	print('\n\n')
	su.print_color(Fore.CYAN, "Great job!\nThe script is now going to attempt to authenticate using the provided information.")
	su.print_color(Fore.CYAN, "\tThis may take a few seconds to process. Just hold on a minute...\n\n")

	try:
		reddit = praw.Reddit(client_id=client_setup['id'], client_secret=client_setup['secret'],
							 password=user_setup['password'], user_agent='RSM-Authenticator', username=user_setup['username'])
		user = reddit.user.me()

		su.print_color(Fore.GREEN, "Authenticated as [%s]\n" % user.name)
		import random
		settings = Settings(settings_file, can_load=False) # Skip loading and just build from defaults.
		settings.set('auth', {
			"client_id": client_setup['id'],
			"client_secret": client_setup['secret'],
			"password": user_setup['password'],
			"user_agent": "RMD-%s" % random.random(),
			"username": user_setup['username']
		})
		settings.save()

		su.print_color(Fore.GREEN, "Well done, it all works!\n"
								   "Your setup is complete!\n"
								   "By default, the program has been configured to scan submissions and comments you've upvoted/saved.")
		if console.confirm('Would you like to set up some other sources?'):
			interact(settings)
		else:
			su.print_color(Fore.GREEN, "Everything's good to go, then! Just relaunch the script to start downloading!")
			sys.exit(0)
	except prawcore.exceptions.ResponseException:
		su.print_color(Fore.RED, "There was an error authenticating you.")
		su.print_color(Fore.RED, "Edit or delete the 'Settings.ini' file just created, then")
		su.print_color(Fore.RED, "retry these steps and assure you've gotten everything correct.")

		sys.exit(1)



def interact(settings):
	""" Used only after base setup to simplify managing Sources and their Filters. Can be run at any time. """
	print("Source wizard launched.\n"
		'ABOUT: "Sources" are the places this downloader pulls Submissions or Comments from.\n'
		"\tThere are many different places on Reddit that you may want to pull posts from.\n"
		"\tThis wizard is built to help you easily manage them.\n")
	while True:
		su.print_color(Fore.GREEN, '=== Config Wizard Home ===')
		opt = console.prompt_list('What would you like to do?',[
			('Edit my saved account information', 'account'),
			('Add a new Source', 'add'),
			('Edit my current Sources (%s)' % len(settings.get_sources()), 'edit_source'),
			("Save & Exit", "exit")
		])
		print('\n\n')

		if opt=='exit':
			settings.save()
			print('Wizard completed.')
			sys.exit(0)

		if opt == 'add':
			_add_source(settings)

		if opt == 'edit_source':
			_edit_sources(settings)

		if opt == 'account':
			_edit_account(settings)

		print('\n\n')



def _edit_account(settings):
	""" Make changes to the saved base account and client details. """
	auth = settings.get('auth')
	print('Leave any lines blank to leave setting unchange:')
	for k, v in auth.items():
		new_val = console.string('\tEnter your new %s' % (k.replace('_', ' ')) )
		if new_val is not None:
			auth[k] = new_val
	if console.confirm('Save these changed values?', False):
		settings.set('auth', auth)
		settings.save()
		print('Changes saved.')
	else:
		print("Changes not saved.")


def _edit_sources(settings):
	""" Called when the User should be promtped for a Source to edit. """
	print()
	sources = settings.get_sources()
	if len(sources) == 0:
		print('You have no sources to edit!')
		return
	targ = console.prompt_list(
		'Which source would you like to edit?',
		[ ('"%s" :: %s' % (s.get_alias(), s.get_config_summary()) , s) for s in sources],
		allow_none=True
	)
	if targ is None:
		return
	print('Selected Source: %s' % targ.get_alias())
	_source_editor(settings, targ)


def _add_source(settings):
	""" Prompts the user for a new Source to add. """
	from sources import source
	all_sources = source.get_sources()
	choice = console.prompt_list(
		"What would you like to download?",
		[(s.description, s.type) for s in all_sources],
		allow_none=True
	)
	print('\n')
	for s in all_sources:
		if s.type == choice:
			if s.setup_wizard():
				print('\nAdding new source...')
				name = wizard_functions.get_unique_alias(settings)
				if not name:
					print('Aborted building Source at User request.')
					return
				s.set_alias(name)
				settings.add_source(s)
				_source_editor(settings, s)
			else:
				print("Setup failed. Not adding Source.")
			return
	print('Invalid selection.')



def _source_editor(settings, source):
	""" The editor screen for a specific Source. """
	source_wizard.SourceEditor(source, settings).run()


if __name__ == '__main__':
	sys.path.insert(0, './sources')
	sys.path.insert(0, './filters')
	interact(Settings('../settings.json', can_load=True, can_save=False))