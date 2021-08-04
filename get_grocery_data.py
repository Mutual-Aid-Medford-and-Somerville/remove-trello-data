import sys, getopt

from trello_utils import *
from trello_api import getCards

config = configparser.ConfigParser()
config.read('config.ini')

REQUESTS_ID = config['MAMAS']['REQUESTS']

def getGroceryCards():
	toFilterList = []
	toFilterList.extend(getAllCards(REQUESTS_ID))

def main(argv):
	getGroceryCards()
	

if __name__ == "__main__":
	main(sys.argv[1:])
