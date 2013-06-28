from copy import copy
from card import Card
from symbols import Direction, Rank, Suit
from deck import Deck


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
    def __init__(self, declarerCards, dummyCards, deck, suit):
        if suit not in Suit:
            raise TypeError, "Expected Suit, got %s" % type(suit)
        self.suit = suit
        self.suitCards = [c for c in deck.cards if c.suit == self.suit]
        self.playedCards = []
        self.suitCards.sort(reverse = True)
        self.suitDeclarerCards = [dc for dc in declarerCards if dc.suit == self.suit]
        self.suitDummyCards = [dc for dc in dummyCards if dc.suit == self.suit]
        self.suitDeclarerCards.sort(reverse = True)
        self.suitDummyCards.sort(reverse = True)
        self.orderedRanks = sorted(Rank, key = lambda x: Rank[x], reverse = True)
# TODO: probably need to add separate codes for defenders leading. I guess not needed for single suit thing. But definitely required for multiple suits. 
        self.declarerLead = 1
        self.dummyLead = 0
        self.initialState = State(self.suitDeclarerCards, self.suitDummyCards)


    def findBreaksInHand(self, hand):
        segmentedHand = []
        cardsSeen = 0
        newSegment = True
        handLength = len(hand)
        while cardsSeen < handLength:
            if newSegment:
                segmentedHand.append([hand[cardsSeen])
            else:
                segmentedHand[-1].append(cardsSeen)

# TODO: Probably will need to be modified based on dynamic rank later
            currentRank = hand[cardsSeen].rank
            nextRank = hand[cardsSeen + 1].rank
            if (Rank[currentRank] == Rank[nextRank] + 1):
                newSegment = False
            else:
                newSegment = True
            cardsSeen += 1
        return segmentedHand

# TODO: Needs to be updated to find all the breaks in the suit
    def findTouchingHonorCards(self):
        i = 0
        j = 0
        k = 0
        limit1 = len(self.suitDeclarerCards)
        limit2 = len(self.suitDummyCards)
        touchingHonors = []
        while i < limit1 and j < limit2:
            if Rank[self.suitDeclarerCards[i].rank] == Rank[self.orderedRanks[k]]:
                touchingHonors.append(self.orderedRanks[k])
                k += 1
                i += 1
            elif Rank[self.suitDummyCards[j].rank] == Rank[self.orderedRanks[k]]:
                touchingHonors.append(self.orderedRanks[k])
                k += 1
                j += 1
            else:
                break
        while i < limit1:
            if Rank[self.suitDeclarerCards[i].rank] == Rank[self.orderedRanks[k]]:
                touchingHonors.append(self.orderedRanks[k])
                k += 1
                i += 1
            else:
                break
        while j < limit2:
            if Rank[self.suitDummyCards[j].rank] == Rank[self.orderedRanks[k]]:
                touchingHonors.append(self.orderedRanks[k])
                k += 1
                j += 1
            else:
                break
        return touchingHonors


# Both this and the next function still need to be here, but we'll have to find some suitable use of these in the overall plan.

    def planForEqualDistribution(self, maxNoOfTricks):
        size = len(self.suitDeclarerCards)
        declarerStart = 0
        declarerEnd = size - 1
        dummyStart = 0
        dummyEnd = size - 1

        moves = [] # We'll store tuples of type (declarer card, dummy card) 
        trickNo = 0
        while trickNo < maxNoOfTricks:
            if Rank[self.suitDeclarerCards[declarerStart].rank] > Rank[self.suitDummyCards[dummyStart].rank]:
                moves.append((self.suitDeclarerCards[declarerStart], self.suitDummyCards[dummyEnd]))
                declarerStart += 1
                dummyEnd -= 1
            else: 
                moves.append((self.suitDeclarerCards[declarerEnd], self.suitDummyCards[dummyStart]))
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

    def finesse(self, finesseType, declarerCards, dummyCards, defenderCards, whoseLead, finesseCard, coverCard, suit):
##############
    #### Need to fill this function. Generally there will be a few possibilities based on type. My idea is that if we are losing, then probably just tell that to the planner. Because it doesn't seem very fruitful to plan if we lose on finesse. Or maybe not. If we win, I guess I should go ahead and plan more. So a recursive call in that case.  
##################


    def cash(self):
        # code to be written. Shoudn't be overly difficult.


    def duck(self):
        # Again the move doesn't seem all that complex. What I'm confused about is how I get a search from here? Do I just worry about one move? or do I worry about the whole search? If the goal is to pull out a high card from the winner, should I just stop after succeeding in doing that? That does seem kind of intelligent.




 #   def ruff(self):
        # this function is not useful in the single suit play, but seems easy enough to code in the normal play. I mean search should take care of other worries, right?     
    




# TODO: Is there some way to infer something about both defenders? I see one fairly easy thing to do will be if one of them is all out in one suit. That seems pretty straight forward. I don't have much more right now.

# TODO: Somewhere in this function I'll have to look for patterns of different kind of plays. Also I'll have to keep track of the lengths in suits. That way I can do the basic counting and use it as a strength.
    def plan(self):
        touchingHonors = self.findTouchingHonorCards()
        declarerLength = len(self.suitDeclarerCards)
        dummyLength = len(self.suitDummyCards)
        if declarerLength == dummyLength:
            maxNoOfTricks = min(len(touchingHonors), declarerLength)
            finalPlan = self.planForEqualDistribution(maxNoOfTricks)
        else:
            finalPlan = self.planForUnequalDistribution(self.suitDeclarerCards, self.suitDummyCards, self.dummyLead, 0, touchingHonors) # TODO:something has to be done for all these honor rank positions stuff and all
        return finalPlan





#def main():
#    c1 = Card('Ace', 'Spade')
#    c2 = Card('King', 'Spade')
#    c3 = Card('Queen', 'Spade')
#    c4 = Card('Jack', 'Spade')
#    c5 = Card('Ten', 'Spade')
#    c6 = Card('Seven', 'Spade')
#    c7 = Card('Six', 'Spade')
#    c8 = Card('Nine', 'Spade')
#    c9 = Card('Eight', 'Spade')
#    c10 = Card('Three', 'Spade')
#    c11 = Card('Five', 'Spade')
#    c12 = Card('Two', 'Spade')
#    c13 = Card('Four', 'Spade')
#    #game = Play([c1, c2, c12], [c3, c4, c13, c10], "Spade")  
#    game = Play([c2, c3, c5, c12], [c1, c4], "Spade")  
#    finalPlan = game.plan()
#    for move in finalPlan:
#        print move
#    if (len(finalPlan) == 0):
#        print "No plan found"
#
#main()
