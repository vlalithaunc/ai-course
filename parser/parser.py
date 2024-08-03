import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP | S Conj S
NP -> N | Det N | Adj NP | NP PP | Det Adj N | NP Conj NP
VP -> V | V NP | VP PP | Adv VP | VP Adv | VP Conj VP
PP -> P NP
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    # perform tokenization
    tokens = nltk.word_tokenize(sentence)

    # lowercase the words
    tokens = [token.lower() for token in tokens]

    # any word that does not contain at lelast one alphabetic character should be excluded
    # so check wehther token is an alphabetic char or not
    tokens = [character for character in tokens if character.isalpha()]
    return tokens


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    nounPhraseChunks = []

    # go through all the subtrees of the tree and find NP chunks
    for subtree in tree.subtrees():
        # check whether the current subtree has a label of 'NP'
        # if so, check whether current subtree does not contain other NPs, otherwise it will be rules out
        if subtree.label() == 'NP':
            containsNounPhrase = False
            # check for every child of subtree
            for child in subtree:
                if isinstance(child, nltk.Tree) and child.label() == 'NP':
                    containsNounPhrase = True
                    break
            # if none of the children of subtree are labeled as NP, then append to list
            if not containsNounPhrase:
                nounPhraseChunks.append(subtree)

    return nounPhraseChunks


if __name__ == "__main__":
    main()
