#Current Issues: Something permanenet has to be done for enums
#TODO: Have to add an attribute for dynamic rank to the Card class. Also, have to figure out efficient way to modify it regularly
#TODO: Possibly can also add an attribute for whether it's an honor card or not.

from Symbols import Rank, Suit

class Card:
    rank = property(lambda self: self.__rank)
    suit = property(lambda self: self.__suit)

    def __init__(self, rank, suit):
        if rank not in Rank:
            raise TypeError, "Expected Rank, got %s" %(rank)
        if suit not in Suit:
            raise TypeError, "Expected Suit, got %s" %(suit)
        self.__rank = rank
        self.__suit = suit  

    def __eq__(self, other):
        """Two cards are equivalent if their ranks and suits match."""
        if isinstance(other, Card):
            return self.suit == other.suit and self.rank == other.rank
        return False


    def __cmp__(self, other):
        """Compare cards for hand sorting.
        
        Care must be taken when comparing cards of different suits.
        """
        if not isinstance(other, Card):
            raise TypeError, "Expected Card, got %s" % type(other)

        selfIndex = Suit[self.suit]*13 + Rank[self.rank]
        otherIndex = Suit[other.suit]*13 + Rank[other.rank]
        return cmp(selfIndex, otherIndex)

    def __repr__(self):
        return "Card(%s, %s)" % (self.rank, self.suit)


    def getStateToCopy(self):
        return self.rank, self.suit


#def main():
#    c1 = Card('Two', 'Spade')
#    print c1.rank
#    print c1.suit
#    print c1.getStateToCopy()
#main()
