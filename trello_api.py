import requests
import json
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

# Personal key and token
TRELLO_KEY = config['TRELLO']['KEY']
TRELLO_TOKEN = config['TRELLO']['TOKEN']

# Headers
headers = {
	'Accept': 'application/json'
}

def getAllCards(boardID):
	response = requests.request(
		'GET',
		f'https://api.trello.com/1/board/{boardID}/cards/all',
		headers=headers,
		params={
			'key': TRELLO_KEY,
			'token': TRELLO_TOKEN
		}
	)

	return json.loads(response.text)

def getCards(listID):
	response = requests.request(
		'GET',
		f'https://api.trello.com/1/lists/{listID}/cards',
		headers=headers,
		params={
			'key': TRELLO_KEY,
			'token': TRELLO_TOKEN
		}
	)
	
	return json.loads(response.text)

def getCardComments(cardID):
	actions = requests.request(
		'GET',
		f"https://api.trello.com/1/cards/{cardID}/actions",
		headers=headers,
		params={
			'key': TRELLO_KEY,
			'token': TRELLO_TOKEN,
			'filter': 'commentCard'
		}
	)

	return actions.json()

def createCard(name, cardListID):
	response = requests.post(
		f"https://api.trello.com/1/cards",
		headers=headers,
		params={
			'key': TRELLO_KEY,
			'token': TRELLO_TOKEN
		},
		data={
			"name": name,
			"idList": cardListID
		},
	)

	return json.loads(response.text)

def archiveCard(cardID):
	response = requests.put(
		f"https://api.trello.com/1/cards/{cardID}",
		headers=headers,
		params={
			'key': TRELLO_KEY,
			'token': TRELLO_TOKEN,
		},
		data={
			"closed": "true"
		}
	)

	return response.status_code

def deleteCard(cardID):
	response = requests.delete(
		f"https://api.trello.com/1/cards/{cardID}",
		headers=headers,
		params={
			'key': TRELLO_KEY,
			'token': TRELLO_TOKEN
		}
	)

	return response.status_code
