from copy import copy
from operator import mul
from random import shuffle

from card import Card
from symbols import Direction, Rank, Suit



#TODO: Delete this function or see if there is really any need for it.
comb = lambda n, k: reduce(mul, range(n, n-k, -1)) / reduce(mul, range(1, k+1))


# TODO: Should hand be made a separate class?
# TODO: I should have an attribute for the high card points also. 

class Deck(object):
    """A Deck object provides operations for dealing Card objects.
    
    A hand is a collection of 13 cards from the deck.
    A deal is a distribution of all 52 cards to four hands.
    
    A deal is represented as a dictionary, mapping Direction labels to
    lists (hands) of Card objects.
    
    """

    cards = [Card(r, s) for r in Rank for s in Suit]
    cardSeq = copy(cards)
    cardSeq.sort(reverse=True)  # Order based on rank and suit

    #TODO: Do I need index of the deal level stuff? I can get rid of it.
    Nmax = comb(52, 13)
    Emax = comb(39, 13)
    Smax = comb(26, 13)
    D = Nmax * Emax * Smax


    #TODO: Do I need this function?
    def isValidDeal(self, deal):
        """Checks that structure of deal conforms to requirements:

          * 4-element dict, mapping Direction objects to hand lists.
          * Hand lists contain exactly 13 Card objects.
          * No card may be repeated in the same hand, or between hands.
          * The cards in hands may be in any order.

        @param deal: a deal dict.
        @return: True if deal is valid, False otherwise.
        """
        return True  # TODO - fill up if you decide to keep this function.


    def randomDeal(self):
        """Shuffles the deck and generates a random deal of hands.
        
        @return: a deal dictionary.
        """
        shuffle(self.cards)
        hands = {}
        for position in Direction:
            hands[position] = []
        for index, card in enumerate(self.cards):
            hands[Direction[index % len(Direction)]].append(card)
        for hand in hands.values():
            hand.sort()
        return hands

