import sys, getopt

from trello_utils import *
from trello_api import archiveCard, deleteCard, getArchivedCards, getCards

config = configparser.ConfigParser()
config.read('config.ini')

def prepareForArchive(card, daysSince):
	return filterByTime(card, getPrepareArchiveDate(daysSince)) and filterByState(card, ('closed', False))

def prepareForDelete(card, daysSince):
	return filterByTime(card, getPrepareDeleteDate(daysSince)) and filterByState(card, ('closed', True))

def archiveProvidedCards(cards):
	for card in cards:
		status = archiveCard(card['id'])
		if status != '200':
			print(f"Failed to archive {card['name']}.")

def deleteProvidedCards(cards):
	for card in cards:
		status = deleteCard(card['id'])
		if status != '200':
			print(f"Failed to delete {card['name']}.")

def checkActions(action, cards):
	print(f"The following are cards that will be {action}d:");
	for idx in range(0, 3):
		print(f"\t{cards[idx]['name']} - {cards[idx]['dateLastActivity']}")
	for idx in range(len(cards)-3, len(cards)-1):
		print(f"\t{cards[idx]['name']} - {cards[idx]['dateLastActivity']}")
	response = input(f"Are you sure you wish to {action} {len(cards)} cards? (y/N)")
	if(str.lower(response) == 'y'):
		return True
	return False

def performArchiveAndDelete(action, daysSince):
	cards = []
	print('Getting cards from "Follow Up"...')
	cards.extend(getCards(getFollowUpList()))
	print('Getting cards from "Needs Met"...')
	cards.extend(getCards(getNeedsMetList()))

	if action == 'archive':
		print('Filtering cards to archive...')
		toArchiveList = list(filter(lambda card: prepareForArchive(card, daysSince), cards))
		canProceed = checkActions(action, toArchiveList)
		if canProceed:
			for card in toArchiveList:
				archiveCard(card['id'])
		else:
			print(f"Skipping {action} and exiting.")
			sys.exit()
	elif action == 'delete':
		print('Preparing cards to delete...')
		cards = getArchivedCards(getBoard())
		toDeleteList = list(filter(lambda card: prepareForDelete(card, daysSince), cards))
		canProceed = checkActions(action, toDeleteList)
		if canProceed:
			for card in toDeleteList:
				deleteCard(card['id'])
		else:
			print(f"Skipping {action} and exiting.")
			sys.exit()
	else:
		print('Action unrecognized. Exiting.')
		sys.exit()

	return

def usage():
	print('Archive or delete Trello data.')
	print('Usage: remove_trello_data.py -a <action> -d <days since report>')
	print('	remove_trello_data.py -h for this dialogue.')
	print('	Can also use --action, --days, and --help.')
	return

def main(argv):
	action = ''
	daysSince = 0
	try:
		opts, args = getopt.getopt(argv,'ha:d:',['help','action=','days='])
	except getopt.GetoptError:
		usage()
		sys.exit(2)
	for opt, arg in opts:
		if opt in ('-h','--help'):
			usage()
			sys.exit()
		elif opt in ('-a','--action'):
			action = arg
		elif opt in ('-d','--days'):
			daysSince = int(arg)

	performArchiveAndDelete(action, daysSince)

if __name__ == "__main__":
	main(sys.argv[1:])
