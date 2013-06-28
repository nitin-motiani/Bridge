# TODO: One property which will be cool for a hand is high card points. But truly speaking I don't see too much use of it. And do we base it on dynamic ranks and update it regularly, or is it one time static thing? 
from copy import copy
from card import Card
from symbols import Direction, Rank, Suit
from math import factorial

class Play(object):
    def __init__(self, declarerCards, dummyCards):
        self.played = {}
        for position in Direction: 
            self.played[position] = []
        self.playedBySuits = {}
        for suit in Suit:
            self.playedBySuits[suit] = []
        self.leftDefenderOver = {}
        self.rightDefenderOver = {}
        self.suitDeclarerCards = {}
        self.suitDummyCards = {}
        for suit in Suit:
            self.suitDeclarerCards[suit] = [dc for dc in declarerCards if dc.suit == suit]
            self.suitDummyCards[suit] = [dc for dc in dummyCards if dc.suit == suit]
            self.suitDeclarerCards[suit].sort(reverse = True)
            self.suitDummyCards[suit].sort(reverse = True)


        for suit in Suit:
            self.leftDefenderOver[suit] = False
            self.rightDefenderOver[suit] = False
        self.orderedRanks = sorted(Rank, key = lambda x: Rank[x], reverse = True)
        self.declarerLead = 1
        self.dummyLead = 0


    def getProbabilities(self, defendersCount, cardsWithLeft, totalOutStandingCards, outStandingInLeft):
        #print defendersCount
        #print cardsWithLeft
        #print totalOutStandingCards
        #print outStandingInLeft
        distributeSuit = factorial(defendersCount)/(factorial(cardsWithLeft)*factorial(defendersCount - cardsWithLeft))
        distributeOthers = factorial(totalOutStandingCards - defendersCount)/(factorial(outStandingInLeft - cardsWithLeft)*factorial(totalOutStandingCards - defendersCount - outStandingInLeft + cardsWithLeft)) 
        totalDistributions = factorial(totalOutStandingCards)/(factorial(outStandingInLeft)*factorial(totalOutStandingCards - outStandingInLeft))
        probability = float(distributeSuit)*distributeOthers/totalDistributions
        return probability
        

    def findBreaksInHand(self, hand):
        segmentedHand = []
        cardsSeen = 0
        newSegment = True
        handLength = len(hand)
        while cardsSeen < handLength:
            if newSegment:
                segmentedHand.append([hand[cardsSeen]])
            else:
                segmentedHand[-1].append(hand[cardsSeen])

# TODO: Probably will need to be modified based on dynamic rank later
            currentRank = hand[cardsSeen].dynamicRank
            if cardsSeen < handLength - 1:
                nextRank = hand[cardsSeen + 1].dynamicRank
            if (nextRank and currentRank == nextRank + 1):
                newSegment = False
            else:
                newSegment = True
            cardsSeen += 1
        return segmentedHand


    # TODO: Probably can be done for getting tempo too
    def getTouchingHonors(self, hand, startingPosition):
        i = 0
        k = startingPosition
        limit = len(hand)
        touchingHonors = []
        while i < limit:
            if hand[i].dynamicRank == Rank[self.orderedRanks[k]]:
                touchingHonors.append(hand[i])
                k += 1
                i += 1
            else:
                break
        return touchingHonors

# TODO: Needs a better method which modifies the dynamic rank of only those cards which are actually going to change. Here lot of redundant work is being done everytime. 
    #def updateDynamicRanks(self, hand, playedInSuit):
    #    if len(playedInSuit) == 0:
    #        return
    #    played = copy(playedInSuit)
    #    played.sort(reverse = True)
    #    r = 0 
    #    j = 0
    #    k = 0
    #    playedLength = len(played)
    #    for k in len(self.orderedRanks):
    #        if (j < playedLength) and (played[j].rank == self.orderedRanks[k]):
    #            j += 1
    #        elif hand[i].rank == self.orderedRanks[k]:
    #            hand[i].dynamicRank = Rank[self.orderedRanks[r]]
    #            i += 1
    #            r += 1
    #        else:
    #            r += 1
    #            

    def useLength(self, declarerCards, dummyCards, suit, remainingCards, numberOfTricksPlayed, whoseLead, plans):
        declarerCardsCopy = copy(declarerCards)
        dummyCardsCopy = copy(dummyCards)
        totalOutStandingCards = 26 - 2*numberOfTricksPlayed
        totalLength = len(declarerCardsCopy) + len(dummyCardsCopy)
        defendersCount = remainingCards - totalLength
        minimumTricksToEmptySuit = defendersCount/2
        declarerLength = len(declarerCards)
        dummyLength = len(dummyCards)
        if self.leftDefenderOver[suit] or self.rightDefenderOver[suit]:
            return []
        else:
            probability = self.getProbabilities(defendersCount, defendersCount/2, totalOutStandingCards, totalOutStandingCards/2)
            if defendersCount%2 == 1:
                probability  = probability * 2
                minimumTricksToEmptySuit += 1
        if len(declarerCards) == len(dummyCards):
            possibleExtraTricks = len(declarerCards) - minimumTricksToEmptySuit 
        else:
            if len(declarerCards) > len(dummyCards):
                longerHand = declarerCardsCopy
                shorterHand = dummyCardsCopy
                shorter = 0
            else:
                longerHand = dummyCardsCopy
                shorterHand = declarerCardsCopy
                shorter = 1
            possibleExtraTricks = len(longerHand) - minimumTricksToEmptySuit
# TODO: VERY VERY URGENT!!!!!!!!!!!!!!!!! make sure that your minimumTricksToEmptySuit is also modified when you remove cards from dummy and declarer. 
        startingPositionForTouchingHonors = 0
        if len(plans) > 0:
            if plans[0][0] == 'finesse':
                for plan in plans:
                    finesseType = plan[1]
                    finesseHand = plan[2]
                    finesseCard = plan[3]
                    coverCard = plan[4]
                    leadCard = plan[5]
                    if finesseHand == 1:
                        declarerCardsCopy.remove(finesseCard)
                        if finesseType == 2: 
                            dummyCardsCopy = dummyCardsCopy[:-1]
                        else:
                            dummyCardsCopy.remove(leadCard)
                    else:
                        dummyCardsCopy.remove(finesseCard)
                        if finesseType == 2:
                            declarerCardsCopy = declarerCardsCopy[:-1]
                        else:
                            declarerCardsCopy.remove(leadCard)
                    minimumTricksToEmptySuit -= 1
            else:
                if plans[0][0] == 'drawOutHonor' and len(plans) > 1 and plans[1][0] == 'finesse' and plans[1][1] == 3:
                    losers = plans[0][1]
                    winners = plans[0][3]
                    if winners >= 2:
                        moves = plans[0][2]
                        for move in moves:
                            declarerMove = move[0]
                            dummyMove = move[1]
                            if type(declarerMove) != type('Discard'):
                                declarerCardsCopy.remove(declarerMove)
                            if type(dummyMove) != type('Discard'):
                                dummyCardsCopy.remove(dummyMove)
                            minimumTricksToEmptySuit -= 1
                            startingPositionForTouchingHonors += 2
                    else:
                        finesseHand = plans[1][2]
                        finesseCard = plan[1][3]
                        leadCard = plans[1][5]
                        if finesseHand == 1:
                            declarerCardsCopy.remove(finesseCard)
                            dummyCardsCopy.remove(leadCard)
                        else:
                            dummyCardsCopy.remove(finesseCard)
                            declarerCardsCopy.remove(leadCard)
                        minimumTricksToEmptySuit -= 1
                else:
                    moves = plans[0][2]
                    for move in moves:
                        declarerMove = move[0]
                        dummyMove = move[1]
                        if type(declarerMove) != type('Discard'):
                            declarerCardsCopy.remove(declarerMove)
                        if type(dummyMove) != type('Discard'):
                            dummyCardsCopy.remove(dummyMove)
                        minimumTricksToEmptySuit -= 1
                        startingPositionForTouchingHonors += 2
        combined = declarerCardsCopy + dummyCardsCopy
        combined.sort(reverse = True)
#TODO: Make sure that this 0 is correct argument or if something else fits better. This might not be correct if you successfully draw out a bigger honor card. In such cases, moves might turn out to be empty. So we just put peace when it comes to extra winners in this one and doesn't really include length in the plan. Also if finesse and draw out both are possible, probably should check it right there and plan for only one thing. If you are gaining nothing from length, pack that from plan.
        touchingHonors = self.getTouchingHonors(combined, startingPositionForTouchingHonors)
        if len(declarerCardsCopy) == len(dummyCardsCopy):
            moves = []
            size = len(declarerCardsCopy)
            maxTricks = min(len(touchingHonors), size)
            declarerStart = 0
            declarerEnd = size - 1
            dummyStart = 0
            dummyEnd = size - 1
            for trickNo in range(maxTricks):
                if Rank[declarerCardsCopy[declarerStart].rank] > Rank[dummyCardsCopy[dummyStart].rank]:
                    moves.append((declarerCardsCopy[declarerStart], dummyCardsCopy[dummyEnd]))
                    declarerStart += 1
                    dummyEnd -= 1
                else: 
                    moves.append((declarerCardsCopy[declarerEnd], dummyCardsCopy[dummyStart]))
                    declarerEnd -= 1
                    dummyStart += 1
            if maxTricks >= minimumTricksToEmptySuit:
                for i in range(maxTricks, size):
                    moves.append((declarerCardsCopy[declarerStart], dummyCardsCopy[dummyStart]))
                lostTricks = 0
                possibleExtraTricks = size - maxTricks
            else:
# TODO: First throw away the tricks then win.
                for i in range(maxTricks, size):
                    moves.append((declarerCardsCopy[declarerEnd], dummyCardsCopy[dummyEnd]))
                lostTricks = minimumTricksToEmptySuit - maxTricks
            
            return ("useLength", moves, probability, lostTricks, possibleExtraTricks)
        else:
            moves = []
            if len(touchingHonors) > 0:
                longerCount = 0
                for th in touchingHonors:
                    if th in longerHand:
                        longerCount += 1
                if longerCount == 0:
                    maxTricks = len(touchingHonors)
                    if shorter == 1:
                        declarerPoint = 0
                        dummyPoint = len(dummyCardsCopy) - 1
                    else:
                        dummyPoint = 0
                        declarerPoint = len(declarerCardsCopy) - 1
                    for i in range(0, maxTricks):
                            moves.append((declarerCardsCopy[declarerPoint], dummyCardsCopy[dummyPoint]))
                            if shorter == 1:
                                declarerPoint += 1
                                dummyPoint -= 1
                            else:
                                declarerPoint -= 1
                                dummyPoint += 1
                    if shorter == 1:
                        declarerPoint = len(shorterHand) - 1
                    else:
                        dummyPoint = len(shorterHand) - 1
                    for i in range(maxTricks, len(shorterHand)):
                        moves.append((declarerCardsCopy[declarerPoint], dummyCardsCopy[dummyPoint]))
                        declarerPoint -= 1
                        dummyPoint -= 1
                    for i in range(len(shorterHand), len(longerHand)):
                        if shorter == 1:
                            moves.append(('Discard', dummyCardsCopy[dummyPoint]))
                            dummyPoint -= 1
                        else:
                            moves.append((declarerCardsCopy[declarerPoint]))
                            declarerPoint -= 1
                    if maxTricks >= minimumTricksToEmptySuit:
                        lostTricks = 0
                        possibleExtraTricks = len(longerHand) - maxTricks
                    else:
                        lostTricks = minimumTricksToEmptySuit - maxTricks
                    return ("useLength", moves, probability, lostTricks, possibleExtraTricks)
                else:
                    sureTricksHere = self.planForUnequalDistribution(declarerCardsCopy, dummyCardsCopy, whoseLead, 0, touchingHonors) 
                    if len(sureTricksHere) >= minimumTricksToEmptySuit:
                        #print "here"
                        #print "sureTricks ", sureTricksHere
                        moves = sureTricksHere
                        lostTricks = 0
                        possibleExtraTricks = len(longerHand) - len(sureTricksHere)
                        for move in moves:
                            declarerMove = move[0]
                            dummyMove = move[1]
                            if type(declarerMove) != type('Discard'):
                                declarerCardsCopy.remove(declarerMove)
                            if type(dummyMove) != type('Discard'):
                                dummyCardsCopy.remove(dummyMove)
                    else:
                        #print "there"
                        #print "sureTricks ", sureTricksHere
                        #print "existing moves ", moves
                        lostTricks = minimumTricksToEmptySuit - len(sureTricksHere)
                        for i in range(0, lostTricks):
                            moves.append((declarerCardsCopy[-1], dummyCardsCopy[-1]))
                            declarerCardsCopy = declarerCardsCopy[:-1]
                            dummyCardsCopy = dummyCardsCopy[:-1]
                        remainingSureTricks = self.planForUnequalDistribution(declarerCardsCopy, dummyCardsCopy, whoseLead, 0, touchingHonors) 
                        #print "remainingSureTricks ", remainingSureTricks
                        for move in remainingSureTricks:
                            declarerMove = move[0]
                            dummyMove = move[1]
                            if type(declarerMove) != type('Discard'):
                                declarerCardsCopy.remove(declarerMove)
                            if type(dummyMove) != type('Discard'):
                                dummyCardsCopy.remove(dummyMove)
                        moves = moves + remainingSureTricks
                    if shorter == 1:
                        for c in dummyCardsCopy:
                            moves.append(('Discard', c))
                    else:
                        for c in declarerCardsCopy:
                            moves.append((c, 'Discard'))
                    return ("useLength", moves, probability, lostTricks, possibleExtraTricks)
            else:
                if shorter == 1:
                    declarerPoint = len(shorterHand) - 1
                    dummyPoint = len(longerHand) - 1
                else:
                    dummyPoint = len(shorterHand) - 1
                    declarerPoint = len(longerHand) - 1
                for i in range(0, len(shorterHand)):
                    moves.append((declarerCardsCopy[declarerPoint], dummyCardsCopy[dummyPoint]))
                    declarerPoint -= 1
                    dummyPoint -= 1
                if shorter == 1:
                    for i in range(len(shorterHand), len(longerHand)):
                        moves.append(('Discard', dummyCardsCopy[dummyPoint]))
                        dummyPoint -= 1
                else:
                    for i in range(len(shorterHand), len(longerHand)):
                        moves.append((declarerCardsCopy[declarerPoint], dummyCardsCopy[dummyPoint]))
                        declarerPoint -= 1
                lostTricks = minimumTricksToEmptySuit
                return ("useLength", moves, probability, lostTricks, possibleExtraTricks)



    def planForExtraTricks(self, declarerCards, dummyCards, requiredNoOfTricks, maxAdmissibleLosses, remainingCards, numberOfTricksPlayed, whoseLead, suit):
        plans = []

        if len(declarerCards) == 0 and len(dummyCards) == 0:
            return plans
        if len(declarerCards) == 0:
            highestCard = dummyCards[0]
            highest = dummyHighest
        elif len(dummyCards) == 0:
            highestCard = declarerCards[0]
            highest = declarerHighest
        else:
            declarerHighest = declarerCards[0].dynamicRank
            dummyHighest = dummyCards[0].dynamicRank
            if declarerHighest > dummyHighest:
                highestCard = declarerCards[0]
                highest = declarerHighest
            else:
                highestCard = dummyCards[0]
                highest = dummyHighest

# TODO: Probably something more generic than 11 required. At least use a variable.
        if highest == 11 or highest == 10:
            startingPosition = 12 - Rank[highestCard.rank]  
            allCards = copy(declarerCards) + copy(dummyCards)
            allCards.sort(reverse = True)
            allCards.remove(highestCard)
            possibleWinners = self.getTouchingHonors(allCards, startingPosition + 1)
            if highestCard in declarerCards:
                declarerMove = highestCard
                remainingDeclarerCards = declarerCards[1:]
                if len(dummyCards) > 0:
                    dummyMove = dummyCards[-1]
                    remainingDummyCards = dummyCards[:-1]
                else:
                    dummyMove = 'Discard'
            else:
                dummyMove = highestCard
                remainingDummyCards = dummyCards[1:]
                if len(declarerCards) > 0:
                    declarerMove = declarerCards[-1]
                    remainingDeclarerCards = declarerCards[:-1]
                else:
                    declarerMove = 'Discard'
# TODO: Add a check to make sure we aren't throwing away one of the possible winners.
            moves = [(declarerMove, dummyMove)]
            if highest == 10:
                anotherLoss = possibleWinners[0]
                if anotherLoss in declarerCards:
                    newDeclarerMove = anotherLoss
                    if len(dummyCards) > 0 and len(remainingDummyCards) > 0 :
                        newDummyMove = remainingDummyCards[-1]
                    else:
                        newDummyMove = 'Discard'
                else:
                    newDummyMove = anotherLoss
                    if len(declarerCards) > 0 and len(remainingDeclarerCards) > 0 :
                        newDeclarerMove = remainingDeclarerCards[-1]
                    else:
                        newDeclarerMove = 'Discard'
                moves.append([newDeclarerMove, newDummyMove])
                possibleWinners = possibleWinners[1:]
                
            # TODO: Probably only useful if you use some sort of method to check that number of possible winnners is gonna be good enough in some sense.
            plans.append(("drawOutHonor", startingPosition, moves, len(possibleWinners)))

        
        finesseType = 0
        finessePossible = False
        completeHand = declarerCards + dummyCards
        completeHand.sort(reverse = True)
        completeSegmentedHand = self.findBreaksInHand(completeHand)

# TODO: get some variable for this 12
        if completeHand[0].dynamicRank == 12 and len(completeSegmentedHand) > 1:
            firstSegmentSmallest = completeSegmentedHand[0][-1].dynamicRank
            secondSegmentLargest = completeSegmentedHand[1][0].dynamicRank
# TODO: Finesse against split honors
            if firstSegmentSmallest - secondSegmentLargest == 2:
                for fc in completeSegmentedHand[1]:
                    finesseCard = fc 
                    if finesseCard in declarerCards:
                        finesseHand = 1         #Declarer
                        for c in completeSegmentedHand[0]:
                            if c in declarerCards:
                                finesseType = 1
                                coverCard = c
                                break
                    else:
                        finesseHand = 0         #Dummy
                        for c in completeSegmentedHand[0]:
                            if c in dummyCards:
                                finesseType = 1
                                coverCard = c
                                break
                    if finesseType == 0:
                        coverCard = completeSegmentedHand[0][0]
                        finesseType = 2
                    if finesseHand == 1:
                        if dummyCards[-1].dynamicRank > finesseCard.dynamicRank:
                            finessePossible = False
                        else:
                            if finesseType == 1:
                                leadCard = dummyCards[-1]
                            else:
                                leadCard = finesseCard
                            finessePossible = True
                    else:
                        if declarerCards[-1].dynamicRank > finesseCard.dynamicRank:
                            finessePossible = False
                        else:
                            if finesseType == 1:
                                leadCard = declarerCards[-1]
                            else:
                                leadCard = finesseCard
                            finessePossible = True
                    if finessePossible:
                        plans.append(("finesse", finesseType, finesseHand, finesseCard, coverCard, leadCard))

# Finesse against the Ace.
        elif completeHand[0].dynamicRank == 11:
            finesseCard = completeHand[0]
            finesseType = 3
            leadCard = finesseCard
            if finesseCard in declarerCards:
                finesseHand = 1     #Declarer
                if len(dummyCards) > 0:
                    finessePossible = True
                    leadCard = dummyCards[-1]
                else:
                    finessePossible = False
            else:
                finesseHand = 0     #Dummy
                if len(declarerCards) > 0:
                    finessePossible = True
                    leadCard = declarerCards[-1]
                else:
                    finessePossible = False
            coverCard = None
            if finessePossible:
                plans.append(("finesse", finesseType, finesseHand, finesseCard, coverCard, leadCard))

        declarerLength = len(declarerCards)
        dummyLength = len(dummyCards)
        totalLength = declarerLength + dummyLength
# TODO: May need to change 7 to some sort of generic number based on how many cards have been played. But this will do for now.
        if totalLength >= remainingCards/2:
            lengthPlan = self.useLength(declarerCards, dummyCards, suit, remainingCards, numberOfTricksPlayed, whoseLead, plans)
            if len(lengthPlan) != 0:
                plans.append(lengthPlan)
        return plans

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
            if (shorterStart <= shorterEnd) and (shorterHand[shorterStart] in touchingHonors) and (Rank[shorterHand[shorterStart].rank] > Rank[longerHand[longerStart].rank]):
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
            elif longerHand[longerStart] in touchingHonors:
                # I think here we can be sure that the shorter one is not the one leading right now
                if (shorterStart > shorterEnd):
                    while longerStart <= longerEnd:
                        if (longerHand[longerStart] in touchingHonors):
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
                        if shorterHand[shorterStart] not in touchingHonors:
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
                        if shorterHand[shorterStart] not in touchingHonors:
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

# TODO: Modify for dynamic rank
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
        #print "here"
        #print declarerCards
        #print dummyCards 
        #print touchingHonors, whoseLead, depth
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
            if (len(declarerCards[suit]) > 0 and declarerCards[suit][0] not in touchingHonors[suit]) and (len(dummyCards[suit]) > 0 and dummyCards[suit][0] not in touchingHonors[suit]):
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
            #print "suit initial plan", suit, possibleInitialPlan
            possibleFinalPlan = possibleInitialPlan + self.planForMultipleSuits(declarerCardsCopy, dummyCardsCopy, touchingHonors, whoseLead, depth + 1)
            if len(possibleFinalPlan) > len(finalPlan):
                finalPlan = possibleFinalPlan
        return finalPlan


    def getSureTricks(self, declarerCards, dummyCards, whoseLead, initialSuit = None):
        touchingHonors = {}
        for suit in Suit:
            totalCards = declarerCards[suit] + dummyCards[suit]
            totalCards.sort(reverse = True)
            touchingHonors[suit] = self.getTouchingHonors(totalCards, 0)
        return self.planForMultipleSuits(self.suitDeclarerCards, self.suitDummyCards, touchingHonors, whoseLead, 0, initialSuit)


    def isHoldUpRequired(declarerCards, dummyCards, touchingHonors):
        totalLength = len(declarerCards) + len(dummyCards)
        if totalLength == 5 or totalLength == 6 or totalLength == 7:
            if len(touchingHonors) == 1 and touchingHonors[0].rank == 12:
                return True
        return False 


    def choosePlan(self, declarerCards, dummyCards, tricksRequired, maxAdmissibleLosses, initialSuit = None):
        sureTricks = self.getSureTricks(declarerCards, dummyCards, self.dummyLead, initialSuit) 
        if len(sureTricks) >= tricksRequired:
            return sureTricks
        extraTricksRequired = tricksRequired - len(sureTricks)
        extraPlans = {}
        touchingHonors = {}
        tempoNeeded = {}
        minTempo = 14
        for suit in Suit:
            totalCards = declarerCards[suit] + dummyCards[suit]
            totalCards.sort(reverse = True)
            touchingHonors[suit] = self.getTouchingHonors(totalCards, 0)
            if len(touchingHonors[suit]) > 0 and len(touchingHonors[suit]) < minTempo:
                minTempo = len(touchingHonors[suit])
            extraPlans[suit] = self.planForExtraTricks(declarerCards[suit], dummyCards[suit], tricksRequired, 13 - tricksRequired, 13, 0, self.dummyLead, suit)
            losers = 0
            for plan in extraPlans[suit]:
                if plan[0] == 'drawOutHonor':
                    losers += plan[1]
                elif plan[0] == 'useLength':
                    losers += plan[3]
                
            if losers > maxAdmissibleLosses: 
                extraPlans[suit] = []
                losers = 0
            tempoNeeded[suit] = losers

        maxProb = 0
        planToFollow = []
        prob = 0
        for suit in Suit:
            if tempoNeeded[suit] <= minTempo:
                for plan in extraPlans[suit]:
                    if plan[0] == 'finesse':
                        prob = 0.5
                    elif plan[0] == 'useLength':
                        prob = plan[2]
                    else:
                        prob = 1
                if prob > maxProb:
                    planToFollow = extraPlans[suit]
        return planToFollow
                    

    # TODO: Finish this. This function should be able to play the deal. 
    def play(self, declarerCards, dummyCards, tricksRequired, maxAdmissibleLosses):
        trickNo = 1
# 2 for lho, 3 for rho, 1 for declarer, 0 for dummy
        lead = 2
        planOngoing = False
        extraPlans = {}
        touchingHonors = {}
        holdUpCounter = {}
            
        while trickNo <= 13:
            for suit in Suit:
                totalCards = declarerCards[suit] + dummyCards[suit]
                totalCards.sort(reverse = True)
                touchingHonors[suit] = self.getTouchingHonors(totalCards)
            if lead == 2 or lead == 3:
                c = defenderMove(lead)
                s = c.suit
                declarerSuitCards = declarerCards[s]
                dummySuitCards = dummyCards[s]
                if lead == 2:
                    whoseLead = self.dummyLead
                else:
                    whoseLead = self.declarerLead
                sureTricks = self.getSureTricks(declarerCards, dummyCards, whoseLead, suit)
                cashingMove = None
                finesseMove = None
                drawOutMove = None
                useLengthMove = None
                holdUpMove = None

                if len(sureTricks) >= tricksRequired:
                    return sureTricks
                if len(sureTricks) > 0:
                    cashingMove = sureTricks[0]
                else:
                    sureTricks = self.getSureTricks(declarerCards, dummyCards, whoseLead)
                extraTricksRequired = tricksRequired - sureTricks
                for suit in Suit:
                    remainingCards = len(13 - self.playedBySuits[suit])
                    extraPlans[suit] = self.planForExtraTricks(declarerCards, dummyCards, tricksRequired, maxAdmissibleLosses, trickNo - 1, whoseLead) 
                possiblePlans = extraPlans[s]
                finesseOverDrawOut = False
                if len(possiblePlans) > 0:
                    i = 0
                    while i < len(possiblePlans):
                        if possiblePlans[i][0] != 'finesse':
                            break
                        if possiblePlans[i][2] == whoseLead:
                            i += 1
                        else:
                            break
                    if i != 0:
                        if possiblePlans[i][0] == 'finesse':
                            finesseMove = possiblePlans[i]
                        else:
                            useLengthMove = possiblePlans[i]
                    elif possiblePlans[0][0] == 'drawOutHonor':
                        drawOutMove = possiblePlans[0]
                        if len(possiblePlans) >= 2 and possiblePlans[1][0] == 'finesse' and possiblePlans[1][1] == 3:
                            finesseMove = possiblePlans[1]
                            losers = possiblePlans[0][1]
                            winners = possiblePlans[0][3]
                        if winners < 2:
                            finesseOverDrawOut = True
                        if finesseOverDrawOut and finesseMove[2] == whoseLead:
                            drawOutMove = None
                            finesseMove = None
                        if len(possiblePlans) == 3:
                            useLengthMove = possiblePlans[2]
                    else :
                        useLengthMove = possiblePlans[0]
                if cashingMove:
# TODO: Most likely need to come up with something better for this.
                    if finesseMove:
                        move = finesseMove
                    elif useLengthMove:
                        useLengthMoves = useLengthMove[1]
                        if useLengthMoves[0][0] in touchingHonors[s] or useLengthMoves[0][1] in touchingHonors[s]:
                            move = cashingMove
                        else:
                # TODO: might need some other checks too.
                            if lostTricks > maxAdmissibleLosses:
                                move = cashingMove
                            else:
                                move = useLengthMove        # Have to chose from this
                    else:
                        if holdUpCounter[s][0]:
                            if holdUpCounter[s][1] == 0:
                                move = cashingMove
                            else:
                                holdUpCounter[s][1] -= 1
                                if len(declarerCards) > 0:
                                    declarerMove = declarerCards[-1]
                                else:
                                    declarerMove = 'Discard'
                                if len(dummyCards) > 0:
                                    dummyMove = dummyCards[-1]
                                else:
                                    dummyCards = 'Discard'
                                move = (declarerMove, dummyMove)
                        else:
                            holdUp = self.isHoldUpRequired(declarerCards, dummyCards, touchingHonors[s])
                            if holdUp:
                                holdUpCounter[s] = [True, 1]
                                if len(declarerCards) > 0:
                                    declarerMove = declarerCards[-1]
                                else:
                                    declarerMove = 'Discard'
                                if len(dummyCards) > 0:
                                    dummyMove = dummyCards[-1]
                                else:
                                    dummyCards = 'Discard'
                                move = (declarerMove, dummyMove)
                            else:
                                move = cashingMove

                else:
                    if finesseMove and drawOutMove:
                        if finesseOverDrawOut:
                            move = finesseMove
                        else:
                            move = drawOutMove
                    elif finesseMove:
                        move = finesseMove
                    elif drawOutMove:
                        move = drawOutMove
                    elif useLengthMove:
                        move = useLengthMove
                    else:
                        if len(declarerCards) > 0:
                            declarerMove = declarerCards[-1]
                        else:
                            declarerMove = 'Discard'
                        if len(dummyCards) > 0:
                            dummyMove = dummyCards[-1]
                        else:
                            dummyCards = 'Discard'
                        move = (declarerMove, dummyMove)
                    if move == finesseMove and finesseHand == whoseLead:
                        move = useLengthMove

            else:
                if lead == 0:
                    whoseLead = self.dummyLead
                else:
                    whoseLead = self.declarerLead

                sureTricks = self.getSureTricks(declarerCards, dummyCards, whoseLead)
                if len(sureTricks) >= tricksRequired:
                    return sureTricks
                extraTricksRequired = tricksRequired - sureTricks
                
# Look at extra plans for all suits.

# Combine all attributes of a plan.

# Count extra tricks and losses for all of them.

# Now select only those where losses are less than admissible and tricks are more than required.

# Say you got competing plans.

# Now how do you decide the frigging suit to take

# If plans starting with losing tricks have enough entries to make up for it, they are contenders. 

# Plans with finesse are contenders too. 

# In plans with possible entries, look at the probability then. 

# Also compare it with probability of finesse too. 

# Don't know how to decide then.

# remove the move taken from your chosen plan. Also remember that this is the plan you have been working with.

# How do you decide when to replan?

# I guess you can replan if you finesse loses.

# If next move you had decided to play from your plan is no longer possible, replan.

                # 3. Else look at the difference. look at the plans in suits, and see which one is good. Again decide is an important factor.
                # 4. I think something about tempo of the shortest or weekest suit should be looked at.

def main():
    c1 = Card('King', 'Spade')
    c2 = Card('Queen', 'Spade')
    c3 = Card('Jack', 'Spade')
    c4 = Card('Ten', 'Spade')
    c5 = Card('Six', 'Spade')
    c6 = Card('Four', 'Spade')
    c7 = Card('Three', 'Spade')
    c8 = Card('Five', 'Spade')
    c9 = Card('Two', 'Spade')
    c10 = Card('Ace', 'Spade')
    c11 = Card('Eight', 'Spade')
    c12 = Card('Seven', 'Spade')
    c13 = Card('Nine', 'Spade')
    c14 = Card('Queen', 'Heart')
    c15 = Card('Jack', 'Heart')
    c16 = Card('Ten', 'Heart')
    c17 = Card('Nine', 'Heart')
    c18 = Card('Eight', 'Heart')
    c19 = Card('Seven', 'Heart')
    c20 = Card('Five', 'Heart')
    c21 = Card('Four', 'Heart')
    c22 = Card('Three', 'Heart')
    c23 = Card('Ace', 'Diamond')
    c24 = Card('King', 'Diamond')
    c25 = Card('Four', 'Diamond')
    c26 = Card('Two', 'Diamond')
    c27 = Card('Ace', 'Club')
    c28 = Card('King', 'Club')
    c29 = Card('Queen', 'Club')
    c30 = Card('Four', 'Club')
    c31 = Card('Three', 'Club')
    c32 = Card('Two', 'Club')

    #extraPlan = game.planForExtraTricks([c6, c7, c9], [c2, c3, c4, c13], 9, 4, 13, 0, 0, 'Spade')
    #print len(extraPlan)
    #print extraPlan
    game = Play([c8, c7, c14, c15, c16, c17, c18, c19, c25, c26, c27, c28, c29], [c1, c2, c3, c6, c9, c20, c21, c22, c23, c24, c30, c31, c32]) 
    planToFollow = game.choosePlan({"Spade": [c8, c7], "Heart": [c14, c15, c16, c17, c18, c19], "Diamond": [c25, c26], "Club": [c27, c28, c29]}, {"Spade": [c1, c2, c3, c6, c9], "Heart": [c20, c21, c22], "Diamond": [c23, c24], "Club": [c30, c31, c32]}, 9, 4)
    print "final ", planToFollow

main()
