from remove_trello_data import prepareForDelete
from trello_utils import getBoard, getFollowUpList, getNeedsMetList, jsonDump
from trello_api import archiveCard, deleteCard, getAllCards, getArchivedCards
from remove_trello_data import prepareForDelete

all_cards = getArchivedCards(getBoard())
print(len(all_cards))

to_delete_list = list(filter(lambda card: prepareForDelete(card, 7), all_cards))
print(len(to_delete_list))