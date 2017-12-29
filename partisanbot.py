
import praw
import time
import os
import requests
import re
# need "comments_replied_to to be global, but before was setting = authenticate, may cause problems now that i'm setting it to empty??"
# should refactor to have Conservative, Liberal, and NDP classes that extend a super class called Party
comments_replied_to = []
conservative_count = 0
conservative_bal = 0
liberal_count = 0
liberal_bal = 0
ndp_count = 0
ndp_bal = 0


def authenticate():
	print("autheticating...")
	reddit = praw.Reddit('partisanbot',
			user_agent = "IExistForTestingBots testBot v0.1")
	print("Authenticated as {}".format(reddit.user.me()))
	return reddit


def count_conservative(body):
	global conservative_count
	conservative_count += 1 
	global conservative_bal
	conservative_bal += count_good_or_bad(body)


def count_liberal(body):
	global liberal_count
	liberal_count +=1
	global liberal_bal
	liberal_bal += count_good_or_bad(body)


def count_ndp(body):
	global ndp_count
	ndp_count +=1
	global ndp_bal
	ndp_bal += count_good_or_bad(body)


# should add body.lower()
def count_good_or_bad(body):
	bal = 0
	if "good" in body or "great" in body or "awesome" in body or "love" in body or "best" in body or "like" in body or "favorite" in body:
		bal += 1
	if "bad" in body or "awful" in body or "hate" in body or "dislike" in body or "worst" in body or "racist" in body or "stupid" in body or "suck" in body or "dumb" in body or "horrible" in body or "terrible" in body or "evil" in body or "creepy" in body or "ugly" in body:
		bal -= 1
	return bal


def is_conservative(body):
	if "cpc" in body or "conservative" in body or "cons" in body or "tory" in body or "harper" in body or "right" in body or "scheer" in body:
		return True
	else:
		return False


def is_liberal(body):
	if "lpc" in body or "liberal" in body or "libs" in body or "grits" in body or "trudeau" in body or "justin" in body or "centre" in body or "center" in body:
		return True
	else: 
		return False


def is_ndp(body):
	if "ndp" in body or "social democrat" in body or "socialist" in body or "new democrat" in body or "left" in body or "labour" in body or "singh" in body or "jagmeet" in body or "mulcair" in body:
		return True
	else:
		return False


def check_username(username, reddit):
	user = reddit.redditor(username)
	try:
		if user.id:
			print("Username Exists")
			return True
	except:
		print("Username Doesn't Exist")
		return False

# not being used
def get_username(body, reddit):
	words_in_comment = body.split()
	#print(words_in_comment)
	for word in words_in_comment:
		print("word")
		print(word)
		if "/u/" in word:
			username = extract_user(word)
			if check_username(username, reddit):
				return username
	return "Error, No Given Username"


def extract_user(word):
	username = word.partition("/u/")[2]
	print("extract_user:")
	print(username)
	return username



# needs refactoring
def parse_comment_history(username, reddit):
	print("username")
	print(username)
	user = reddit.redditor(username)
	
	for comment in user.comments.new(limit=None):
		print(comment.body)	

		if is_conservative(comment.body.lower()):
			count_conservative(comment.body.lower())

		if is_liberal(comment.body.lower()):
			count_liberal(comment.body.lower())

		if is_ndp(comment.body.lower()):
			count_ndp(comment.body.lower())	

	global conservative_count
	global conservative_bal
	global liberal_count
	global liberal_bal
	global ndp_count
	global ndp_bal

	comment_reply = "Comments mentioning the Conservatives: " + str(conservative_count) + "  Balance: " + str(conservative_bal) + "\n"
	comment_reply += "Comments mentioning the Liberals: " + str(liberal_count) + "  Balance: " + str(liberal_bal) + "\n"
	comment_reply += "Comments mentioning the NDP: " + str(ndp_count) + "  Balance: " + str(ndp_bal)
	return comment_reply


def run_bot(reddit):
	for comment in reddit.subreddit('test').comments(limit=25):
		if r"/u/" and "!partisanshipBot" in comment.body and comment.id not in comments_replied_to and comment.author != reddit.user.me():
			
			comment_reply = "Hi, I'm the partisan bot, and I'm here to to assess your partisanship!\n\n"
			username = get_username(comment.body, reddit)
			comment_reply += parse_comment_history(username, reddit)
			comment.reply(comment_reply)
			print("Replied to comment " + comment.id)
			comments_replied_to.append(comment.id)

			with open("comments_replied_to.txt", "a") as f:
				f.write(comment.id + "\n")

	print("sleep for 10 seconds")
	#Sleep for 10 seconds
	time.sleep(10)


def get_saved_comments():
	if not os.path.isfile("comments_replied_to.txt"):
		comments_replied_to = []
	else:
		with open("comments_replied_to.txt", "r") as f:
			comments_replied_to = f.read()
			comments_replied_to = comments_replied_to.split("\n")
			comments_replied_to = filter(None, comments_replied_to)

	return comments_replied_to


def main():
	reddit = authenticate()
	comments_replied_to = get_saved_comments()
	while True:
		run_bot(reddit)


if __name__ == '__main__':
	main()