import requests
import json
import os
import configparser

from mdutils import MdUtils
from datetime import date
from datetime import datetime
from datetime import timedelta

config = configparser.ConfigParser()
config.read(os.environ['CONFIG'])

DELETE_DAYS = 28
ARCHIVE_DAYS = 28

# Sam stuff
TRELLO_KEY = config['TRELLO']['KEY']
TRELLO_TOKEN = config['TRELLO']['TOKEN']

# Tech team board.
REQUESTS_ID = config['MAMAS']['REQUESTS']

# Cards in board.
FOLLOW_UP_ID = config['BOARDS']['FOLLOW_UP']
NEED_MET_ID = config['BOARDS']['NEED_MET']

# Headers
headers = {
	'Accept': 'application/json'
}

def jsonDump(one_card):
	print(json.dumps(one_card, sort_keys=True, indent=4, separators=(",", ": ")))

def getLastActivity(card):
	lastActivityISOStr = card['dateLastActivity'][0:10]
	return date.fromisoformat(lastActivityISOStr)

def filterByState(card, setting):
	return card[setting[0]] == setting[1]

def filterByTime(card, dayThreshold):
	lastActivity = getLastActivity(card)
	relevantTimespan = timedelta(days=dayThreshold)
	return (date.today() - lastActivity) >= relevantTimespan

def filterToArchive(card):
	return filterByTime(card, ARCHIVE_DAYS) and filterByState(card, ('closed', False))

def filterToDelete(card):
	return filterByTime(card, DELETE_DAYS) and filterByState(card, ('closed', True))

def toDeleteReport(card):
	report = {}

	# Get name, list, and labels
	report['name'] = card['name']

	if (card['idList'] == FOLLOW_UP_ID):
		report['list'] = 'Follow Up'
	elif (card['idList'] == NEED_MET_ID):
		report['list'] = 'Need Met'
	else:
		report['list'] = 'Unknown'

	report['labels'] = list(map(lambda label: label['name'], card['labels']))

	# Fetch recent comments
	actions = requests.request(
		'GET',
		'https://api.trello.com/1/cards/%s/actions'%(card['id']),
		headers=headers,
		params={
			'key': TRELLO_KEY,
			'token': TRELLO_TOKEN,
			'filter': 'commentCard'
		}
	)
	comments = actions.json()

	# Set recent comment based on returned comment list
	if (len(comments) > 0):
		report['recentComment'] = comments[0]['data']['text']
	else:
		report['recentComment'] = card['desc']

	# Add the last updated date
	report['lastUpdate'] = getCardDate(card).isoformat()

	return report

def generateMdFile(cardInfo, reportType):
	datestr = datetime.now().strftime('%Y-%m-%d')
	reportname = f"{reportType}-{datestr}-report"

	print('Generating %s...'%(reportname))
	mdFile = MdUtils(file_name=reportname,title='Today\'s Trello Report')

	# Intro text
	mdFile.write('Hey tech-team! Here’s a snapshot of what we’re working on based on our current Trello! ')
	mdFile.write('If you have updates you want to give or are interested in following up with/joining some of this work,')
	mdFile.write('either ask here, message the folks on the task, or get in the Trello yourself and see what’s going on!')
	mdFile.new_line()
	mdFile.new_line()

	for card in cardInfo:
		# Card Title
		print('Creating entry for %s...'%(card['name']))
		mdFile.write('**%s**'%(card['name']))

		# Card Tags
		if (len(card['labels']) > 0):
			mdFile.write(' (')
			for i in range(len(card['labels'])):
				mdFile.write('%s'%(card['labels'][i]))
				if (i != len(card['labels'])-1):
					mdFile.write(', ')
			mdFile.write(')')

		# Names on the card
		if (len(card['members']) > 0):
			mdFile.write(' [')
			for i in range(len(card['members'])):
				mdFile.write('%s'%(card['members'][i]))
				if (i != len(card['members'])-1):
					mdFile.write(', ')
			mdFile.write(']')

		# Recent comment
		if (len(card['recentComment']) > 0):
			mdFile.write(': ')
			mdFile.write('%s'%card['recentComment'])
		else:
			mdFile.write(': No further information (someone should add some comments/users)!')

		# Lines between files
		mdFile.new_line()
		mdFile.new_line()

	# Create file
	mdFile.create_md_file()
	print('Done!')

def getCards(listID):
	response = requests.request(
		'GET',
		'https://api.trello.com/1/lists/%s/cards'%(listID),
		headers=headers,
		params={
			'key': TRELLO_KEY,
			'token': TRELLO_TOKEN
		}
	)

	return json.loads(response.text)

cards = []
cards.extend(getCards(FOLLOW_UP_ID))
cards.extend(getCards(NEED_MET_ID))

#filteredList = list(filter(filterToDelete, cards))
filteredList = list(filter(filterToArchive, cards))

for card in filteredList:
	print(jsonDump(card))

# deleteReportList = list(map(lambda card: toDeleteReport(card), filteredList))
 
#for card in deleteReportList:
#	print(card)

#generateMdFile(cardInfo)
