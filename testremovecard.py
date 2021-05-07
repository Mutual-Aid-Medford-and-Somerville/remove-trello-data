from trellorequests import archiveCard, deleteCard, createCard
from trelloeditutils import getFollowUpList

def testArchiveDelete():
	testCard = createCard('test-archive-delete-name', getFollowUpList())

	print(archiveCard(testCard['id']))
	
	print(deleteCard(testCard['id']))

	return

testArchiveDelete()