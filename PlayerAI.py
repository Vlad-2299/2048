from random import randint
from BaseAI import BaseAI
from sys import maxsize
import math
import time

timeLimit = 0.2
vectors = {
    0: (-1, 0),  # up
    1: (0, 1),  # right
    2: (1, 0),  # down
    3: (0, -1)  # left
}


class PlayerAI(BaseAI):

    def min_value(self, state, depth, alpha, beta, v):
        stateCopy = state.clone()

        if v is not None:
            stateCopy.move(v)

        if depth == 0:
            return None, self.evaluate(stateCopy)

        (minChild, minUtility) = (-1, beta)

        for child in stateCopy.getAvailableMoves():
            newState = stateCopy.clone()
            (_, utility) = self.max_value(newState, depth - 1, alpha, minUtility, child)

            if utility < minUtility:
                (minChild, minUtility) = (child, utility)

            if minUtility <= alpha:
                break

            if minUtility < beta:
                beta = minUtility

        return minChild, minUtility

    def max_value(self, state, depth, alpha, beta, v):
        stateCopy = state.clone()

        if v is not None:
            stateCopy.move(v)

        if depth == 0:
            return None, self.evaluate(stateCopy)

        (maxChild, maxUtility) = (-1, alpha)

        for child in stateCopy.getAvailableMoves():
            newState = stateCopy.clone()
            (_, utility) = self.min_value(newState, depth - 1, maxUtility, beta, child)

            if utility > maxUtility:
                (maxChild, maxUtility) = (child, utility)

            if maxUtility >= beta:
                break

            if maxUtility > alpha:
                alpha = maxUtility

        return maxChild, maxUtility

    def findFarthestPosition(self, state, cell, vector):
        while True:
            previous = cell
            cell = (previous[0] + vector[0], previous[1] + vector[1])
            if state.crossBound(cell):
                return previous
            if state.canInsert(cell) is False:
                return cell

    def smoothness(self, state):
        smoothness = 0
        bonus = 0
        stateCopy = state.clone()

        for x in range(stateCopy.size):
            for y in range(stateCopy.size):
                if stateCopy.canInsert((x, y)) is False:
                    value = math.log(stateCopy.getCellValue((x, y))) / math.log(2)
                    # value = stateCopy.getCellValue((x, y))
                    for direction in [1, 2]:
                        vector = vectors[direction]
                        targetCell = self.findFarthestPosition(stateCopy, (x, y), vector)

                        nextCellValue = stateCopy.getCellValue(targetCell)
                        if nextCellValue == stateCopy.getCellValue((x, y)):
                            bonus += math.log(nextCellValue)

                        if stateCopy.canInsert(targetCell) is False:
                            # target = stateCopy.getCellValue(targetCell)
                            targetValue = math.log(nextCellValue) / math.log(2)
                            smoothness -= abs(value - targetValue)
                            # smoothness -= abs(value-target)
        return smoothness, bonus

    def monotonicity(self, state):
        totals0 = 0
        totals1 = 0
        totals2 = 0
        totals3 = 0
        stateCopy = state.clone()

        for y in range(stateCopy.size):
            current = 0
            next = current + 1
            while next < 4:
                while next < 4 and stateCopy.canInsert((next, y)):
                    next += 1
                if next >= 4:
                    next -= 1

                if stateCopy.canInsert((current, y)) is False:
                    currentValue = math.log(stateCopy.getCellValue((current, y))) / math.log(2)
                    # currentValue = stateCopy.getCellValue((current, y))
                else:
                    currentValue = 0

                if stateCopy.canInsert((next, y)) is False:

                    nextValue = math.log(stateCopy.getCellValue((next, y))) / math.log(2)
                    # nextValue = stateCopy.getCellValue((next, y))
                else:
                    nextValue = 0

                if currentValue > nextValue:
                    totals2 += nextValue - currentValue
                elif nextValue > currentValue:
                    totals3 += currentValue - nextValue

                current = next
                next += 1

        for x in range(stateCopy.size):
            current = 0
            next = current + 1
            while next < 4:
                while next < 4 and stateCopy.canInsert((x, next)):
                    next += 1
                if next >= 4:
                    next -= 1
                if stateCopy.canInsert((x, current)) is False:
                    currentValue = math.log(stateCopy.getCellValue((x, current))) / math.log(2)
                    # currentValue = stateCopy.getCellValue((x, current))
                else:
                    currentValue = 0

                if stateCopy.canInsert((x, next)) is False:
                    nextValue = math.log(stateCopy.getCellValue((x, next))) / math.log(2)
                    # nextValue = stateCopy.getCellValue((x, next))
                else:
                    nextValue = 0

                if currentValue > nextValue:
                    totals0 += nextValue - currentValue
                elif nextValue > currentValue:
                    totals1 += currentValue - nextValue

                current = next
                next += 1
        return max(totals0, totals1) + max(totals2, totals3)

    def evaluate(self, state):
        stateCopy = state.clone()
        emptyCells = len(stateCopy.getAvailableCells())
        if emptyCells == 0:
            emptyCells=1
        maxTile = stateCopy.getMaxTile()

        smoothWeight = 0.8
        monoWeight = 2.0
        emptyWeight = 2.7
        maxWeight = 1.0
        if maxTile >= 1024:
            maxWeight += math.log(maxTile) * 7
        (smoothness, bonus) = self.smoothness(stateCopy)

        hSum = smoothness * smoothWeight + self.monotonicity(stateCopy) * monoWeight + math.log(emptyCells) * emptyWeight + maxTile * maxWeight
        # hSum += bonus
        return hSum

    def decision(self, state):
        gridCopy = state.clone()
        iniTime = time.clock()
        depth = 1
        while time.clock() - iniTime < 0.1:
            depth += 1
            print(depth)
            (child, _) = self.max_value(gridCopy, depth, -maxsize, maxsize, None)
        return child

    def getMove(self, grid):

        gridCopy = grid.clone()
        child = self.decision(gridCopy)
        return child