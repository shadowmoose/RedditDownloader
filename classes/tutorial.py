import stringutil as su
from colorama import Fore
import webbrowser
import praw
import prawcore
import sys
from settings import Settings


def run(settings_file='settings.json'):
	client_setup = {'secret':None, 'id':None}
	user_setup = {'username':None, 'password':None}

	su.print_color(Fore.GREEN, "Welcome to the Reddit Media Downloader automatic setup!")
	su.print_color(Fore.YELLOW, '\tThis program will help you automatically set everything up in a few steps.')

	su.print_color(Fore.CYAN, "To start, we need to register this script with reddit.")
	su.print_color(Fore.YELLOW, "\tReddit requires that any program accessing it is registered.")
	su.print_color(Fore.YELLOW, "\tFor your account's security, you need to do this yourself.")

	su.print_color(Fore.CYAN, "Open https://www.reddit.com/prefs/apps, and sign in.")
	if 'y' in input('\tIs it okay to open the URL in your browser for you? (y/n): ').lower():
		webbrowser.open('https://www.reddit.com/prefs/apps')

	su.print_color(Fore.CYAN, "Once you're signed in, scroll down and click on 'Create Application'.")
	print()
	su.print_color(Fore.CYAN, "Give it a name to remind you what it's for in the future, and select the 'Script' option.\n")
	su.print_color(Fore.YELLOW, "The description can be anything to remind yourself.")
	su.print_color(Fore.YELLOW, "The URL and URI fields don't matter, so they can be set to 'http://localhost', or a made-up URL.")
	print('\n')
	su.print_color(Fore.YELLOW, "Go ahead and click 'Create App' after you've filled this all in, then press Enter here.")
	input('[Press Enter to continue]')

	su.print_color(Fore.CYAN, "Now that you've registered your script, scroll to it on the page and get its ID (the random text under 'personal use script' on top of its box)")
	su.print_color(Fore.YELLOW, "\t(This is your client_id)")
	client_setup['id'] = input("Paste or type your client ID here: ").strip()

	su.print_color(Fore.CYAN, "\nAlso grab the generated 'Secret'.")
	su.print_color(Fore.YELLOW, "\t(This is your client_secret)")
	client_setup['secret'] = input("Paste or type your client Secret here: ").strip()

	su.print_color(Fore.RED, "Excellent!\nNow, finally, this script will need the username and password of the account you'd like to scan.")
	su.print_color(Fore.RED, "\tYour credentials will be stored locally, and never sent anywhere - don't worry;")
	su.print_color(Fore.RED, "\tThe whole point of the last few steps was to keep your information safe!")

	user_setup['username'] = input('Enter your username: ')
	user_setup['password'] = input('Enter your password: ')
	print('\n\n')
	su.print_color(Fore.CYAN, "Great job!\nThe script is now going to attempt to authenticate using the provided information.")
	su.print_color(Fore.CYAN, "\tThis may take a few seconds to process. Just hold on a minute...\n\n")

	try:
		reddit = praw.Reddit(client_id=client_setup['id'], client_secret=client_setup['secret'],
							 password=user_setup['password'], user_agent='RSM-Authenticator', username=user_setup['username'])
		user = reddit.user.me()

		su.print_color(Fore.GREEN, "Authenticated as [%s]\n" % user.name)

		settings = Settings(settings_file, can_save=False) # Will be overridden to save.
		settings.set('auth', {
			"client_id": client_setup['id'],
			"client_secret": client_setup['secret'],
			"password": user_setup['password'],
			"user_agent": "RMD-User-Agent",
			"username": user_setup['username']
		})
		settings.save(override_save=True)

		su.print_color(Fore.GREEN, "Well done, it all works!\n"
								   "Your setup is complete!\n"
								   "The main script should new start up. Enjoy!\n\n")
	except prawcore.exceptions.ResponseException:
		su.print_color(Fore.RED, "There was an error authenticating you.")
		su.print_color(Fore.RED, "Please retry these steps and assure you've gotten everything correct.")
		sys.exit(1)
#

run()