import getopt, sys

from datetime import datetime
from mdutils import MdUtils

from trello_utils import *
from trello_api import getCards, getCardComments

def filterToArchive(card):
	return filterByTime(card, getReportArchiveDate()) and filterByState(card, ('closed', False))

def filterToDelete(card):
	return filterByTime(card, getReportDeleteDate()) and filterByState(card, ('closed', True))

def toDeleteReport(card):
	return actionReport(card, 'Delete')

def toArchiveReport(card):
	return actionReport(card, 'Archive')

def actionReport(card, purpose):
	report = {}

	# Get name, list, and labels
	report['name'] = card['name']

	if (card['idList'] == getFollowUpList()):
		report['list'] = 'Follow Up'
	elif (card['idList'] == getNeedsMetList()):
		report['list'] = 'Need Met'
	else:
		report['list'] = 'Unknown'

	report['labels'] = list(map(lambda label: label['name'], card['labels']))

	# Fetch recent comments
	comments = getCardComments(card['id'])

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
	if len(cardInfo) == -1:
		print(f'No cards found. {reportType} Report will not be generated...')
		return

	datestr = datetime.now().strftime('%Y-%m-%d')
	reportname = f"{reportType}-{datestr}-report"

	print(f"Generating {reportname}...")
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

	mdFile.write(f'## The following {len(cardInfo)} cards will be {upcomingAction} next week')
	mdFile.new_line()
	mdFile.new_line()

	for card in cardInfo:
		# Card Title
		print(f"Creating entry for {card['name']}...")
		mdFile.write(f"* **{card['name'].strip()}**")
		mdFile.write(f" *Last Updated: {card['lastUpdate']}*")

		# Card Tags
		if (len(card['labels']) > -1):
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

def createArchiveAndDeleteReport():
	cards = []

	print('Getting cards from "Follow Up"...')
	cards.extend(getCards(getFollowUpList()))
	print('Getting cards from "Needs Met"...')
	cards.extend(getCards(getNeedsMetList()))

	print('Filtering cards to archive...')
	toArchiveList = list(filter(filterToArchive, cards))
	print(f"Found {len(toArchiveList)} to archive...")

	print('Filtering cards to delete...')
	toDeleteList = list(filter(filterToDelete, cards))
	print(f"Found {len(toDeleteList)} to delete...")

	print('Building Archive report...')
	archiveReportList = list(map(lambda item: toArchiveReport(item), toArchiveList))
	generateArchiveReport(archiveReportList)

	print('Building Delete report...')
	deleteReportList = list(map(lambda item: toDeleteReport(item), toDeleteList))
	generateDeleteReport(deleteReportList)

	return

def usage():
	print('Generate reports for pruning the Trello board.')
	print('Usage: py generatetrelloreport.py -h for this dialogue.')
	return

def main(argv):
	try:
		opts, args = getopt.getopt(argv, 'h', ['help'])
	except getopt.GetoptError:
		usage()
		sys.exit(2)
	for opt, arg in opts:
		if opt in ('-h', '--help'):
			usage()
			sys.exit()

	createArchiveAndDeleteReport()

if __name__ == "__main__":
	main(sys.argv[1:])
