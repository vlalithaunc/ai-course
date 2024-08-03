import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # in the sentence, if the number of cells is equal to the count,
        # then return the set of cells as you know all of them have to be mines
        if len(self.cells) == self.count and self.count != 0:
            return self.cells
        # else you are not sure which one is a mine or not, so return empty set
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # if the count is zero, then you know that there are no mines
        # so the set of safe cells will be self.cells
        if self.count == 0:
            return self.cells
        # else you are not sure which are safe or not
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # if a cell is in the cells set and you know it is a mine,
        # then remove the cell from the set of cells
        # and depreciate count (as 'count' represents the num of mines)
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # if the cell is in the cells set and you know its safe,
        # then remove from the list of cells
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # add cell to the moves made
        self.moves_made.add(cell)

        # the move could have been made only if cell is safe to move to,
        # so now we know that we can mark as safe
        self.mark_safe(cell)

        # keep track of the cells we are not sure of
        notSureCells = set()
        # check the surrounding/neighboring cells
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # ignore the cell if its the cell you are currently on
                # check constraints of cells location, then also check whether it is a safe or not
                # then append to unsure list if its not a mine
                if (i, j) != 1 and 0 <= i < self.height and 0 <= j < self.width:
                    # if one of the surrounding cells is a mine, then increment mine count
                    if (i, j) in self.mines:
                        count -= 1
                    else:
                        notSureCells.add((i, j))
        notSureCells -= self.safes
        notSureCells -= self.mines
        # with the new information, create a new sentence, with the unknown cells as the self.cells
        # and count being the previous count of mines - the newly discovered mines
        newSentence = Sentence(notSureCells, count)
        # append this new sentence to knowledge base
        self.knowledge.append(newSentence)

        # go through the knowledge base and update the information on board
        for sentence in self.knowledge:
            # mark any additional cells as safe or mines, based on the AI's knowledge base
            if sentence.known_mines():
                known_mines = sentence.known_mines().copy()
                for cell in known_mines:
                    self.mark_mine(cell)
            if sentence.known_safes():
                known_safes = sentence.known_safes().copy()
                for cell in known_safes:
                    self.mark_safe(cell)

        # go through the knowledge base and update the information on board
        deducedSentences = []
        # now check whether the cells in new sentence is already a part of another sentence cells in the knowledge base
        for sentence1 in self.knowledge:
            for sentence2 in self.knowledge:
                # now take the difference between the list of cells
                if sentence1 != sentence2 and sentence1.cells.issubset(sentence2.cells):
                    new_cells = sentence2.cells - sentence1.cells
                    new_count = sentence2.count - sentence1.count
                    # form a new sentence taking the difference, pass in the different cells and the difference of the count
                    deduced_sentence = Sentence(new_cells, new_count)
                    if deduced_sentence not in self.knowledge and deduced_sentence not in deducedSentences:
                        deducedSentences.append(deduced_sentence)

        self.knowledge.extend(deducedSentences)

        for sentence in self.knowledge:
            # mark any additional cells as safe or mines, based on the AI's knowledge base
            if sentence.known_mines():
                known_mines = sentence.known_mines().copy()
                for cell in known_mines:
                    self.mark_mine(cell)
            if sentence.known_safes():
                known_safes = sentence.known_safes().copy()
                for cell in known_safes:
                    self.mark_safe(cell)

        # remove any empty sets in knowledge base
        empty_sentence = Sentence(set(), 0)
        self.knowledge = [sentence for sentence in self.knowledge if sentence != empty_sentence]

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # to make safe move, check all the cells in the self.safe, then
        # check whether move has been made or not, and return the cell
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
        # if no cell is safe, then return 'None'
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # to make a random move, search through all cells and find the available moves
        availableMoves = []
        for i in range(self.height):
            for j in range(self.width):
                # before adding cell to available moves list, check whether its not a mine
                # or has not been made before
                if (i, j) not in self.moves_made and (i, j) not in self.mines:
                    availableMoves.append((i, j))
        # as long as the number of moves in list is not zero, return a random move
        if len(availableMoves) != 0:
            # randomly choice one of the available moves
            return random.choice(availableMoves)
        return None
