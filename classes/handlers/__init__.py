from classes.handlers import generic_newspaper
from classes.handlers import github
from classes.handlers import imgur
from classes.handlers import reddit_handler
from classes.handlers import ytdl


""" A list of all available static Handlers, pre-sorted by order. """
sorted_list = sorted([
	generic_newspaper, github, imgur, reddit_handler, ytdl
], key=lambda x: x.order, reverse=False)
