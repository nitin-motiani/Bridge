from copy import copy
from card import Card
from symbols import Direction, Rank, Suit


# TODO: This class doesn't seem very useful now. Either find its use in the next step of the work, or delete it. 
class State(object):
    """ We store both declarer and dummy card lists here
        These lists need not be lists of all cards, but can be lists of 
        some subset of cards for example a particular suit
    """
    def __init__(self, declarerCards, dummyCards):
        """
        @param declarerCards: list of declarer cards
        @type declarerCards: list of Card
        @param dummyCards: list of dummy cards
        @type dummyCards: list of Card
        Both lists should be sorted.
        """
        self.declarerCards = declarerCards
        self.dummyCards = dummyCards
    
class Play(object):
    def __init__(self, declarerCards, dummyCards):
        #if suit not in Suit:
        #    raise TypeError, "Expected Suit, got %s" % type(suit)
        #self.suit = suit
        self.suitDeclarerCards = {}
        self.suitDummyCards = {}
        for suit in Suit:
            self.suitDeclarerCards[suit] = [dc for dc in declarerCards if dc.suit == suit]
            self.suitDummyCards[suit] = [dc for dc in dummyCards if dc.suit == suit]
            self.suitDeclarerCards[suit].sort(reverse = True)
            self.suitDummyCards[suit].sort(reverse = True)
        self.orderedRanks = sorted(Rank, key = lambda x: Rank[x], reverse = True)
        self.declarerLead = 1
        self.dummyLead = 0
        self.initialState = State(self.suitDeclarerCards, self.suitDummyCards) # useless as of now


    def findTouchingHonorCards(self, suit):
        if suit not in Suit:
            return
            # TODO: Write some typerror here and do proper exception handling
        i = 0
        j = 0
        k = 0
        limit1 = len(self.suitDeclarerCards[suit])
        limit2 = len(self.suitDummyCards[suit])
        touchingHonors = []
        while i < limit1 and j < limit2:
            if Rank[self.suitDeclarerCards[suit][i].rank] == Rank[self.orderedRanks[k]]:
                touchingHonors.append(self.orderedRanks[k])
                k += 1
                i += 1
            elif Rank[self.suitDummyCards[suit][j].rank] == Rank[self.orderedRanks[k]]:
                touchingHonors.append(self.orderedRanks[k])
                k += 1
                j += 1
            else:
                break
        while i < limit1:
            if Rank[self.suitDeclarerCards[suit][i].rank] == Rank[self.orderedRanks[k]]:
                touchingHonors.append(self.orderedRanks[k])
                k += 1
                i += 1
            else:
                break
        while j < limit2:
            if Rank[self.suitDummyCards[suit][j].rank] == Rank[self.orderedRanks[k]]:
                touchingHonors.append(self.orderedRanks[k])
                k += 1
                j += 1
            else:
                break
        return touchingHonors

    def planForEqualDistribution(self, maxNoOfTricks, declarerCards, dummyCards):
        size = len(declarerCards)
        declarerStart = 0
        declarerEnd = size - 1
        dummyStart = 0
        dummyEnd = size - 1

        moves = [] # We'll store tuples of type (declarer card, dummy card) 
        trickNo = 0
        while trickNo < maxNoOfTricks:
            if Rank[declarerCards[declarerStart].rank] > Rank[dummyCards[dummyStart].rank]:
                moves.append((declarerCards[declarerStart], dummyCards[dummyEnd]))
                declarerStart += 1
                dummyEnd -= 1
            else: 
                moves.append((declarerCards[declarerEnd], dummyCards[dummyStart]))
                declarerEnd -= 1
                dummyStart += 1
            trickNo += 1
        return moves


    def planForUnequalDistribution(self, declarerCards, dummyCards, whoseLead, honorRankPosition, touchingHonors):
        moves = []
        totalTricsTaken = 0
        declarerLength = len(declarerCards)
        dummyLength = len(dummyCards)
        if declarerLength > dummyLength: 
            shorterHand = dummyCards
            longerHand = declarerCards
            shorter = 0
        else:
            shorterHand = declarerCards
            longerHand = dummyCards
            shorter = 1

        shorterStart = 0
        longerStart = 0
        if (shorter == 1):
            shorterEnd = declarerLength - 1
            longerEnd = dummyLength - 1
        else:
            shorterEnd = dummyLength - 1
            longerEnd = declarerLength - 1

        for trickNo in range(0, max(declarerLength, dummyLength)):
            if (whoseLead == self.declarerLead and declarerLength - trickNo <= 0):
                break
            if (whoseLead == self.dummyLead and dummyLength - trickNo <= 0):
                break
            # TODO: This seems like the best possible way. Still, have to see how good it works.
            if (shorterStart <= shorterEnd) and (shorterHand[shorterStart].rank in touchingHonors) and (Rank[shorterHand[shorterStart].rank] > Rank[longerHand[longerStart].rank]):
                if (shorter == 1):
                    move = (shorterHand[shorterStart], longerHand[longerEnd])
                    nextLead = self.declarerLead
                else:
                    move = (longerHand[longerEnd], shorterHand[shorterStart])
                    nextLead = self.dummyLead
                moves.append(move)
                shorterStart += 1
                longerEnd -= 1
                whoseLead = nextLead
                totalTricsTaken += 1
                honorRankPosition += 1  #important to keep modifying this
            # TODO: this is a bit of troubling situation. We haven't taken care of the case with the gap in the shorter suit. Have to do something
            elif longerHand[longerStart].rank in touchingHonors:
                # I think here we can be sure that the shorter one is not the one leading right now
                if (shorterStart > shorterEnd):
                    while longerStart <= longerEnd:
                        if (longerHand[longerStart].rank in touchingHonors):
                            if (shorter == 1):
                                move = ("Discard", longerHand[longerStart])
                            else:
                                move = (longerHand[longerStart], "Discard")
                            moves.append(move)
                            longerStart += 1
                            totalTricsTaken += 1
                            honorRankPosition += 1
                        else:
                            break
                else:
                    if shorter == 1:
                        possibleMove1 = (shorterHand[shorterStart], longerHand[longerEnd])
                        if shorterHand[shorterStart].rank not in touchingHonors:
                            tricks1 = 0
                            futureMoves1 = []
                        else:
                            if (Rank[shorterHand[shorterStart].rank] > Rank[longerHand[longerEnd].rank]):
                                lead = self.declarerLead
                            else:
                                lead = self.dummyLead
                            futureMoves1 = self.planForUnequalDistribution(declarerCards[shorterStart + 1:shorterEnd + 1], dummyCards[longerStart:longerEnd], lead, honorRankPosition, touchingHonors)
                            tricks1 = len(futureMoves1) + 1

                        possibleMove2 = (shorterHand[shorterEnd], longerHand[longerStart])
                        futureMoves2 = self.planForUnequalDistribution(declarerCards[shorterStart:shorterEnd], dummyCards[longerStart + 1:longerEnd + 1], self.dummyLead, honorRankPosition + 1, touchingHonors)
                        tricks2 = 1 + len(futureMoves2)
                    else:
                        possibleMove1 = (longerHand[longerEnd], shorterHand[shorterStart])
                        if shorterHand[shorterStart].rank not in touchingHonors:
                            tricks1 = 0
                            futureMoves1 = []
                        else:
                            if (Rank[shorterHand[shorterStart].rank] > Rank[longerHand[longerEnd].rank]):
                                lead = self.dummyLead
                            else:
                                lead = self.declarerLead
                            futureMoves1 = self.planForUnequalDistribution(declarerCards[longerStart:longerEnd], dummyCards[shorterStart + 1:shorterEnd + 1], lead, honorRankPosition, touchingHonors)
                            tricks1 = len(futureMoves1) + 1

                        possibleMove2 = (longerHand[longerStart], shorterHand[shorterEnd])
                        futureMoves2 = self.planForUnequalDistribution(declarerCards[longerStart + 1:longerEnd + 1], dummyCards[shorterStart:shorterEnd], self.declarerLead, honorRankPosition + 1, touchingHonors)
                        tricks2 = 1 + len(futureMoves2)

                    if (tricks1 > tricks2):
                        moves.append(possibleMove1)
                        moves = moves + futureMoves1
                    else:
                        moves.append(possibleMove2)
                        moves = moves + futureMoves2
                break
            else:
                break
        return moves

    def whatToDiscard(self, cards, suit, touchingHonors):
        cardToDiscard = None
        for s in Suit:
            if s == suit:
                continue
            if (len(cards[s]) > 0) and (cards[s][-1] not in touchingHonors[s]):
                if (not cardToDiscard) or (Rank[cards[s][-1].rank] < Rank[cardToDiscard.rank]):
                    cardToDiscard = cards[s][-1]
        if cardToDiscard:
            return cardToDiscard
        for s in Suit:
            if s == suit:
                continue
            if (len(cards[s]) > 0) and (not cardToDiscard) or (Rank[cards[s][-1].rank] < Rank[cardToDiscard.rank]):
                cardToDiscard = cards[s][-1]

        
    def planForMultipleSuits(self, declarerCards, dummyCards, touchingHonors, whoseLead, depth, initialSuit = None):
        #if depth == 15:
        #    return []
        print "here"
        print declarerCards
        print dummyCards 
        print touchingHonors, whoseLead, depth
        declarerLength = {}
        dummyLength = {}
        finalPlan = []
        for suit in Suit:
            declarerLength[suit] = len(declarerCards[suit])
            dummyLength[suit] = len(dummyCards[suit])

        if (initialSuit and initialSuit in Suit):
            if declarerLength[initialSuit] == dummyLength[initialSuit]:
                maxNoOfTricks = min(len(touchingHonors[initialSuit]), declarerLength[initialSuit])
                initialPlan = self.planForEqualDistribution(maxNoOfTricks, declarerCards[initialSuit], dummyCards[initialSuit])
            else:
                initialPlan = self.planForUnequalDistribution(declarerCards[initialSuit], dummyCards[initialSuit], whoseLead, 0, touchingHonors[initialSuit])
            if (len(initialPlan)) == 0:
                return finalPlan

            if type(initialPlan[-1][0]) == type('Discard'):
                whoseLead = self.dummyLead
            elif type(initialPlan[-1][1]) == type('Discard'):
                whoseLead = self.declarerLead
            elif Rank[initialPlan[-1][0].rank] > Rank[initialPlan[-1][1].rank]:
                whoseLead = self.declarerLead
            else:
                whoseLead = self.dummyLead


            trickNo = 0
            for move in initialPlan:
                declarerMove = move[0]
                dummyMove = move[1]
                if type(declarerMove) != type('Discard'):
                    declarerCards[initialSuit].remove(declarerMove)
                else:
                    cardToDiscard = self.whatToDiscard(declarerCards, suit, touchingHonors)
                    initialPlan[trickNo] = (cardToDiscard, move[1])
                    declarerCards[cardToDiscard.suit].remove(cardToDiscard)
                if type(dummyMove) != type('Discard'):
                    dummyCards[initialSuit].remove(dummyMove)
                else:
                    cardToDiscard = self.whatToDiscard(dummyCards, suit, touchingHonors)
                    initialPlan[trickNo] = (move[0], move[1])
                    dummyCards[cardToDiscard.suit].remove(cardToDiscard)
                trickNo += 1
            finalPlan = initialPlan + self.planForMultipleSuits(declarerCards, dummyCards, touchingHonors, whoseLead, depth + 1)
            return finalPlan

        possibleInitialPlan = []
        for suit in Suit: 
            if whoseLead == 1 and len(declarerCards[suit]) == 0:
                continue
            if whoseLead == 0 and len(dummyCards[suit]) == 0:
                continue
            if (len(declarerCards[suit]) > 0 and declarerCards[suit][0].rank not in touchingHonors[suit]) and (len(dummyCards[suit]) > 0 and dummyCards[suit][0].rank not in touchingHonors[suit]):
                continue
            declarerCardsCopy = {}
            dummyCardsCopy = {}
            # As this is shallow copy, we have to separately copy lists for all the suits
            # I sincerely hope that this suit in suit loop doesn't cause any trouble
            for suit2 in Suit:
                declarerCardsCopy[suit2] = copy(declarerCards[suit2])
                dummyCardsCopy[suit2] = copy(dummyCards[suit2])
            if declarerLength[suit] == dummyLength[suit]:
                maxNoOfTricks = min(len(touchingHonors[suit]), declarerLength[suit])
                possibleInitialPlan = self.planForEqualDistribution(maxNoOfTricks, declarerCards[suit], dummyCards[suit])
            else:
                possibleInitialPlan = self.planForUnequalDistribution(declarerCards[suit], dummyCards[suit], whoseLead, 0, touchingHonors[suit]) # TODO:something has to be done for all these honor rank positions stuff and all
            if len(possibleInitialPlan) == 0:
                continue

            if type(possibleInitialPlan[-1][0]) == type('Discard'):
                whoseLead = self.dummyLead
            elif type(possibleInitialPlan[-1][1]) == type('Discard'):
                whoseLead = self.declarerLead
            elif Rank[possibleInitialPlan[-1][0].rank] > Rank[possibleInitialPlan[-1][1].rank]:
                whoseLead = self.declarerLead
            else:
                whoseLead = self.dummyLead

            trickNo = 0
            for move in possibleInitialPlan:
                declarerMove = move[0]
                dummyMove = move[1]
                if type(declarerMove) != type('Discard'):
                    declarerCardsCopy[suit].remove(declarerMove)
                else:
                    cardToDiscard = self.whatToDiscard(declarerCardsCopy, suit, touchingHonors)
                    possibleInitialPlan[trickNo] = (cardToDiscard, move[1])
                    declarerCardsCopy[cardToDiscard.suit].remove(cardToDiscard)

                if type(dummyMove) != type('Discard'):
                    dummyCardsCopy[suit].remove(dummyMove)
                else:
                    cardToDiscard = self.whatToDiscard(dummyCardsCopy, suit, touchingHonors)
                    possibleInitialPlan[trickNo] = (move[0], cardToDiscard)
                    dummyCardsCopy[cardToDiscard.suit].remove(cardToDiscard)

                trickNo += 1
            print "suit initial plan", suit, possibleInitialPlan
            possibleFinalPlan = possibleInitialPlan + self.planForMultipleSuits(declarerCardsCopy, dummyCardsCopy, touchingHonors, whoseLead, depth + 1)
            if len(possibleFinalPlan) > len(finalPlan):
                finalPlan = possibleFinalPlan
        return finalPlan


    def plan(self):
        touchingHonors = {}
        for suit in Suit:
            touchingHonors[suit] = self.findTouchingHonorCards(suit)
        return self.planForMultipleSuits(self.suitDeclarerCards, self.suitDummyCards, touchingHonors, self.dummyLead, 0, "Diamond")

def main():
    c1 = Card('Ace', 'Spade')
    c2 = Card('King', 'Spade')
    c3 = Card('Eight', 'Spade')
    c4 = Card('Seven', 'Spade')
    c5 = Card('Six', 'Spade')
    c6 = Card('Five', 'Spade')
    c7 = Card('Ace', 'Heart')
    c8 = Card('King', 'Heart')
    c9 = Card('Queen', 'Heart')
    c10 = Card('Jack', 'Heart')
    c11 = Card('Ten', 'Heart')
    c12 = Card('Nine', 'Heart')
    c13 = Card('Queen', 'Spade')
    c14 = Card('Jack', 'Spade')
    c15 = Card('Two', 'Heart')
    c16 = Card('Five', 'Heart')
    c17 = Card('Ace', 'Club')
    c18 = Card('King', 'Club')
    c19 = Card('Jack', 'Club')
    c20 = Card('Ten', 'Club')
    c21 = Card('Nine', 'Club')
    c22 = Card('Six', 'Club')
    c23 = Card('Five', 'Club')
    c24 = Card('Four', 'Club')
    c25 = Card('Three', 'Club')
    c26 = Card('Two', 'Club')
    game = Play([c1, c2, c3, c7, c8, c9, c14, c15, c16, c17, c24, c25, c26], [c4, c5, c6, c10, c11, c12, c13, c18, c19, c20, c22, c22, c23])  
    finalPlan = game.plan()
    for move in finalPlan:
        print move
    if (len(finalPlan) == 0):
        print "No plan found"

main()
