from trello_api import archiveCard, createCard, deleteCard
from trello_utils import getFollowUpList


def testArchiveDelete():
    testCard = createCard("test-archive-delete-name", getFollowUpList())

    print(archiveCard(testCard["id"]))

    print(deleteCard(testCard["id"]))

    return


testArchiveDelete()
