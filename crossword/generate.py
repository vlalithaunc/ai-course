import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # node consistency is achieved when, for every variable, each variable in
        # its domain is consistent with the variables unary constraints

        for variable in self.domains:
            remove_words = []
            # make sure that every word in the variable's domain has same num of letters
            # as the variable's length (slots)
            for word in set(self.domains[variable]):
                # if the length of word does not match the variable length,
                # append to remove words list
                if variable.length != len(word):
                    remove_words.append(word)

            for word in remove_words:
                # then remove word from list of specific variable
                self.domains[variable].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # initialize boolean var to track whether revision has been made or not
        revised = False
        # var x is arc consistent with var y when every value in domain of x has possible value
        # in domain of y, that does not cause conflict (cell between two variables does not disagree with character)

        # call overlaps function to see what overlaps for variables x and y
        overlap = self.crossword.overlaps[x, y]
        if not overlap:
            return False

        letterx, lettery = overlap
        # track which words to remove
        remove_values = set()

        # for every value in the self.domains for variable x
        for word_x in self.domains[x]:
            consistent = False
            for word_y in self.domains[y]:
                # check whether the overlap has the same character, if so, then we are good
                if word_x[letterx] == word_y[lettery]:
                    consistent = True
                    break
            # if the word was not consistent and had conflicts, then add to remove values
            if not consistent:
                remove_values.add(word_x)

        # iterate through remove words list and take them out of domain for variable
        for word_x in remove_values:
            self.domains[x].remove(word_x)
            revised = True

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # if arcs are None, have an initial list of all arcs in the problem
        if arcs is None:
            arcs = []
            for x in self.crossword.variables:
                for y in self.crossword.neighbors(x):
                    arcs.append((x, y))
        else:
            # use 'arcs' as the inital list of arcs to make consistent
            arcs = list(arcs)

        # while there are arcs in the list and we iterate through them
        while arcs:
            # pop first one of the arcs from the queue
            (x, y) = arcs.pop(0)
            # call revise function on x, y variables, and if it is true, continue

            if self.revise(x, y):
                # in the process of enforcing arc consistency using revise, if we remove
                # all the remaining values from the domain (length of domain is 0), then
                # return False, as it is impossible to solve the problem as there are no more
                # possible values for the variable
                if len(self.domains[x]) == 0:
                    return False
                # since we made a change to the domain, we need to add additional arcs to the queue
                # to ensure that the arcs stay consistent

                # so for all the 'y' variables that resulted in true for self.revise, we need to
                # remove them from the self.cross.neighbors(x) and add arcs using other vars
                for another_var in (self.crossword.neighbors(x) - self.domains[y]):
                    arcs.append((another_var, x))
        return False

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # assignment is complete if every crossword variable is assigned to value
        # iterate over each crossword variable
        for variable in self.crossword.variables:
            # if the variable is not in the assignment, then crossword not complete
            if variable not in assignment:
                return False
        # if all variables are assigned, then the assignment is complete
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # assignment is consistent when words fit in crossword puzzle without conflicting characters
        previously_seen = set()
        for variable, word in assignment.items():
            # all values of the assignment must be distinct (so word should not have been seen before)
            if word not in previously_seen:
                previously_seen.add(word)
            else:
                # if there are duplicates, then return false
                return False

            # every value (word) of the assignment must have the correct length as variable
            if len(word) != variable.length:
                return False

            # check the neighboring words/variables
            for neighbor in self.crossword.neighbors(variable):
                # if the neighbor is in the assignment
                if neighbor in assignment:
                    # check the overlapping cell of both the current variable and neighboring variable
                    letteri, letterj = self.crossword.overlaps[variable, neighbor]
                    # if the overlapping letter does not match, then it is a conflicting character
                    if assignment[variable][letteri] != assignment[neighbor][letterj]:
                        # so, the assignment is not consistent
                        return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # this function is designed to order domain value of given variable, according to
        # least constraining heuristic

        # heuristic helps solver by preferring values that rule out the fewest choieces for neighboring values

        # any variable present in assignment already has a value, and therfore should not be counted
        # when computing number of values ruled out for neighboring unassigned values
        conflicts = {}

        unassigned_neighbors = self.crossword.neighbors(var) - set(assignment.keys())

        # iterate through the list of values in the domain of 'var'
        for value in self.domains[var]:
            # initialize the conflicts for a value to be zero (num values ruling out per word)
            conflicts[value] = 0
            # for every neighbor of unassigned neighbors list
            for neighbor in unassigned_neighbors:
                # check the overlap between the variable present and neighboring variable
                overlap = self.crossword.overlaps[var, neighbor]
                if overlap is not None:
                    # (i, j) square is the overlap
                    letterx, lettery = overlap
                    # count the number of values of the neighbor would be invalid if chosen
                    # check for all other words in the neighboring variable, to see which values to rule out
                    for another_value in self.domains[neighbor]:
                        # check for which words there would be a conflict in characters
                        if value[letterx] != another_value[lettery]:
                            # keeps track of the conflicts by neighboring values per value in self.domain[var]
                            conflicts[value] += 1

        # return list of values by num of conflicts they cause
        return sorted(self.domains[var], key=lambda x: conflicts[x])

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_vars = []
        # first add all the variables that are not within assignment to the unassigned list
        for variable in self.crossword.variables:
            if variable not in assignment:
                unassigned_vars.append(variable)

        # initialize variable for storing the variable with minimum remainig values
        # set to positive infinity, as we want to iterate through all the unassigned vars
        # and find the minimum, so compare with a initially high value first
        min_values = float('inf')
        # variable to store this var
        chosen_var = None
        # iterate through all the unassigned variables
        for variable in unassigned_vars:
            # if the length of the remaining values of variable is less than the current min remaining values
            # then replace min_values with the length of remaining values of current 'variable'
            if len(self.domains[variable]) < min_values:
                min_values = len(self.domains[variable])
                # set the chosen unassigned variable as the chosen variable
                chosen_var = variable
            # otherwise, if the length of remaning values equals the min values
            elif len(self.domains[variable]) == min_values:
                # check for the degree, and based on which degree is higher, change the chosen variable
                max_degree = -1
                if min_values is None or len(self.crossword.neighbors(variable)) > len(self.crossword.neighbors(chosen_var)):
                    chosen_var = variable
        return chosen_var

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # first check whether assignment is complete or not, if so return it
        if self.assignment_complete(assignment):
            return assignment

        # else check whether there are unassigned variables in crossword, choose one to begin with
        variable = self.select_unassigned_variable(assignment)

        # try to iterate through values with fewest conflicts with neighboring values first
        for value in self.order_domain_values(variable, assignment):
            # make a copy of assignment for next step
            copy_assignment = assignment.copy()
            # set the next step of the assignment to the variable you have chosen and the value
            copy_assignment[variable] = value
            # check whether the assignment becomes consistent after adding a certain value,
            # if it is not consistent after iterating through all values, then return None
            if self.consistent(copy_assignment):
                # backtracking is recursive search algorithm, after assigning a value to a variable
                # algorithm recursively attempts to assign values to other variables of assignment
                # so explored the consequences of the current assignment
                potential_path = self.backtrack(copy_assignment)
                # checks whether the current assignment leads to a solution
                # if the back track is not None, it indicates that the recursive search found a valid
                # complete assignment from this point forward
                if potential_path is not None:
                    return potential_path

                # if it does not have a solution with the current assignment
                # remove the variable assignment that did not lead to a successful result
                copy_assignment.pop(variable)

        # no assignment possible, then just return none
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
