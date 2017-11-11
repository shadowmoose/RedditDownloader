import stringutil as su
from colorama import Fore
import webbrowser
import praw
import prawcore
import sys
from settings import Settings
import console

def run(settings_file='settings.json'):
	client_setup = {'secret':None, 'id':None}
	user_setup = {'username':None, 'password':None}

	su.print_color(Fore.GREEN, "Welcome to the Reddit Media Downloader automatic setup!")
	su.print_color(Fore.YELLOW, '\tThis program will help you automatically set everything up in a few steps.')

	su.print_color(Fore.CYAN, "To start, we need to register this script with reddit.")
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

	su.print_color(Fore.RED, "Excellent!\nNow, finally, this script will need the username and password of the account you'd like to scan.")
	su.print_color(Fore.RED, "\tYour credentials will be stored locally, and never sent anywhere - don't worry;")
	su.print_color(Fore.RED, "\tThe whole point of the last few steps was to keep your information safe!")

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
			"user_agent": "RMD-"+random.random(),
			"username": user_setup['username']
		})
		settings.save()

		su.print_color(Fore.GREEN, "Well done, it all works!\n"
								   "Your setup is complete!\n"
								   "By default, the program has been configured to scan posts and comments you've upvoted/saved.")
		if console.confirm('Would you like to set up some other sources?'):
			source_wizard(settings)
		else:
			su.print_color(Fore.GREEN, "Everything's good to go, then! Just relaunch the script to start downloading!")
			sys.exit(0)
	except prawcore.exceptions.ResponseException:
		su.print_color(Fore.RED, "There was an error authenticating you.")
		su.print_color(Fore.RED, "Please retry these steps and assure you've gotten everything correct.")
		sys.exit(1)



def source_wizard(settings):
	""" Used only after base setup to simplify managing Sources and their Filters. Can be run at any time. """
	print("Source wizard launched.\n"
		'"Sources" are the places this downloader pulls Posts or Comments from.\n'
		"There are many different places on Reddit that you may want to pull posts from.\n"
		"This wizard is built to help you easily manage them.")
	while True:
		sources = settings.get_sources()
		print("\n\n\nSources loaded: %s" % len(sources) )
		opt = console.prompt_list('What would you like to do?',[
			('Edit my saved account information', 'account'),
			('Edit my current Sources', 'edit_source'),
			('Add a new Source', 'add'),
			("Save & Exit", "exit")
		])
		print("Selected: ", opt)

		if opt=='exit':
			settings.save()
			print('Wizard completed.')
			sys.exit(0)

		if opt == 'edit_source':
			print()
			targ = console.prompt_list(
				'Which source would you like to edit?',
				[ ('"%s" :: %s' % (s.get_alias(), s.get_config_summary()) , s.get_alias()) for s in sources],
				allow_none=True
			)
			if targ is None:
				continue
			print('Selected Source: %s' % targ)
			#TODO: Trigger Source editor function menu.
		#TODO: Set up other options.


def _edit_account():
	pass#TODO: Set up


def _edit_source():
	pass#TODO: Set up


def _add_source():
	pass#TODO: Set up


if __name__ == '__main__':
	sys.path.insert(0, './sources')
	sys.path.insert(0, './filters')
	source_wizard(Settings('../settings.json', can_load=True, can_save=False))