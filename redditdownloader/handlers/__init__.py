from handlers import github, imgur, generic_newspaper
from handlers import reddit_handler
from handlers import ytdl


""" A list of all available static Handlers, pre-sorted by order. """
sorted_list = sorted([
	generic_newspaper, github, imgur, reddit_handler, ytdl
], key=lambda x: x.order, reverse=False)
