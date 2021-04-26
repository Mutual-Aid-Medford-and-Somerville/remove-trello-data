import requests
import json
import os
import configparser

from mdutils import MdUtils
from datetime import date
from datetime import datetime
from datetime import timedelta

config = configparser.ConfigParser()
config.read('config.ini')

DELETE_DAYS = 28
ARCHIVE_DAYS = 28

# Personal key and token
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
	return actionReport(card, 'Delete')

def toArchiveReport(card):
	return actionReport(card, 'Archive')

def actionReport(card, purpose):
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

	report['recentComment'] = " ".join(report['recentComment'].split())[0:150]

	# Add the last updated date
	report['lastUpdate'] = getLastActivity(card)

	return report

def generateDeleteReport(cardInfo):
	generateReport(cardInfo, 'Delete')

def generateArchiveReport(cardInfo):
	generateReport(cardInfo, 'Archive')

def generateReport(cardInfo, reportType):
	if len(cardInfo) == 0:
		print(f'No cards found. {reportType} Report will not be generated...')
		return

	datestr = datetime.now().strftime('%Y-%m-%d')
	reportname = f"{reportType}-{datestr}-report"

	print('Generating %s...'%(reportname))
	mdFile = MdUtils(file_name=reportname, title=f'# {reportType} Report for {datestr}')
	mdFile.new_line()

	# Intro text
	if reportType  == 'Archive':
		mdFile.write(f'The following is a list of cards that will be Archived a week after the creation of this report (on {datestr}). ')
		mdFile.write('Archived Trello cards are still accessible within the application, but they are hidden from normal view. ')
		mdFile.write('Archival means that these cards will be deleted from Trello next month if nothing changes, in accordance with the tech-team data privacy policy. ')
		mdFile.write('If you wish to preserve these cards going forward, please update them in the Trello. If updated, the card will no longer be slated for archival during the upcoming Archive run. ')
		mdFile.write('Please reach out to the tech-team if you have any questions about this policy or Trello Archival.')
	elif reportType == 'Delete':
		mdFile.write(f'The following is a list of cards that will be Deleted a week after the creation of this report (on {datestr}). ')
		mdFile.write('Deleted Trello cards are removed from the service entirely, and any associated data will be gone. ')
		mdFile.write('As per the tech-team privacy policy, we only will delete Archived cards that have not been recently updated. ')
		mdFile.write('Therefore, if you wish to preserve this card, please un-archive it. ')
		mdFile.write('However, please consider allowing it to be deleted. We would prefer to keep as little data on our community members as possible. ')
		mdFile.write('Cards that have not been updated a week after this report is published will be deleted. ')
	else:
		print(f"Unrecognized report type: {reportType}. Exiting...")
		return
		
	mdFile.write('Please reach out to the tech-team if you have any questions about the privacy policy, these reports, or our Trello clean-up actions.')
	mdFile.new_line()
	mdFile.new_line()

	upcomingAction = 'Archived' if reportType == 'Archive' else 'Deleted'
	
	mdFile.write(f'## The following cards will be {upcomingAction} next week')
	mdFile.new_line()
	mdFile.new_line()

	for card in cardInfo:
		# Card Title
		print(f"Creating entry for {card['name']}...")
		mdFile.write(f"* **{card['name'].strip()}**")
		mdFile.write(f" *Last Updated: {card['lastUpdate']}*")

		# Card Tags
		if (len(card['labels']) > 0):
			mdFile.write(' (')
			for i in range(len(card['labels'])):
				mdFile.write(f"{card['labels'][i]}")
				if (i != len(card['labels'])-1):
					mdFile.write(', ')
			mdFile.write(')')

		# Recent comment
		if (len(card['recentComment']) > 0):
			mdFile.write(': ')
			mdFile.write(f"{card['recentComment']}")
		else:
			mdFile.write(': No further information (someone should add some comments/users)!')

		# Lines between files
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

print('Getting cards from "Follow Up"...')

cards.extend(getCards(FOLLOW_UP_ID))

print('Getting cards from "Needs Met"...')

cards.extend(getCards(NEED_MET_ID))

print('Filtering cards to archive...')

toArchiveList = list(filter(filterToArchive, cards))

print('Filtering cards to delete...')

toDeleteList = list(filter(filterToDelete, cards))

print('Building Archive list...')

archiveReportList = list(map(lambda item: toArchiveReport(item), toArchiveList))

print('Building Delete list...')
 
deleteReportList = list(map(lambda item: toDeleteReport(item), toDeleteList))

generateArchiveReport(archiveReportList)
generateDeleteReport(deleteReportList)