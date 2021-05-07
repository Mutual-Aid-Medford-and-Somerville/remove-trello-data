import os

from trelloeditutils import *
from trellorequests import archiveCard, deleteCard, getCards

config = configparser.ConfigParser()
config.read('config.ini')

def prepareForArchive(card):
	return filterByTime(card, getPrepareArchiveDate()) and filterByState(card, ('closed', False))

def prepareForDelete(card):
	return filterByTime(card, getPrepareDeleteDate()) and filterByState(card, ('closed', True))

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

def performArchiveAndDelete():
	cards = []
	print('Getting cards from "Follow Up"...')
	cards.extend(getCards(getFollowUpList()))
	print('Getting cards from "Needs Met"...')
	cards.extend(getCards(getNeedsMetList()))
	print('Filtering cards to archive...')
	toArchiveList = list(filter(prepareForArchive, cards))
	print('Filtering cards to delete...')
	toDeleteList = list(filter(prepareForDelete, cards))

	for card in toArchiveList:
		archiveCard(card['id'])

	for card in toDeleteList:
		deleteCard(card['id'])

	return

# performArchiveAndDelete()