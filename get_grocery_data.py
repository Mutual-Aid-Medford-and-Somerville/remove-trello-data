import sys, getopt

from trello_utils import *
from trello_api import getCards, getAllCards

config = configparser.ConfigParser()
config.read('config.ini')

REQUESTS_ID = config['MAMAS']['REQUESTS']

def getGroceryCards():
	toFilterList = list(filter(lambda card: filterByLabel(card, 'Supplies/Errands'), getAllCards(REQUESTS_ID)))
	toFilterList = list(filter(filterByRespondedLists, toFilterList))
	toFilterList = list(filter(lambda card: filterByDateBound(card, '2021-03-21'), toFilterList))
	return toFilterList

def main(argv):
	cards = getGroceryCards()
	followUpCards = list(filter(lambda card: card['idList'] == getFollowUpList(), cards))
	ongoingCards = list(filter(lambda card: card['idList'] == getOngoingNeedList(), cards))
	needsMetCards = list(filter(lambda card: card['idList'] == getNeedsMetList(), cards))
	print(f"Ongoing Grocery Cards since 03/21/2021: {len(ongoingCards)}")
	print(f"Needs Met Grocery Cards since 03/21/2021: {len(needsMetCards)}")
	print(f"Follow Up Grocery Cards since 03/21/2021: {len(followUpCards)}")
	
if __name__ == "__main__":
	main(sys.argv[1:])
