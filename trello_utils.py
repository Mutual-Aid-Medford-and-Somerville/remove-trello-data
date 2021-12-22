import json
import os
import configparser

from datetime import date
from datetime import timedelta

config = configparser.ConfigParser()
config.read('config.ini')

DELETE_DAYS = 28
ARCHIVE_DAYS = 28
PREVIOUS_WEEK = 7

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

def filterByDateBound(card, dateString):
	lastActivity = getLastActivity(card)
	dateBound = date.fromisoformat(dateString)
	return lastActivity > dateBound

def filterByLabel(card, labelName):
	cardLabels = list(map(lambda label: label['name'], card['labels']))
	return labelName in cardLabels

def filterByRespondedLists(card):
	return card['idList'] == getFollowUpList() or card['idList'] == getNeedsMetList() or card['idList'] == getOngoingNeedList()

def getBoard():
	return config['MAMAS']['REQUESTS']

def getFollowUpList():
    return config['BOARDS']['FOLLOW_UP']

def getNeedsMetList():
    return config['BOARDS']['NEED_MET']

def getOngoingNeedList():
    return config['BOARDS']['ONGOING_NEED']

def getReportArchiveDate():
    return ARCHIVE_DAYS

def getReportDeleteDate():
    return DELETE_DAYS

def getPrepareDeleteDate(adjustByDays=PREVIOUS_WEEK):
    return getReportDeleteDate() + adjustByDays

def getPrepareArchiveDate(adjustByDays=PREVIOUS_WEEK):
    return getReportArchiveDate() + adjustByDays
