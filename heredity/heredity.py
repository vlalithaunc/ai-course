import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def check_genes(person, one_gene, two_genes):
    """
    Returns the number of genes a person has from their parents.
    """
    # check whether the person is in the one_gene or two_genes dictionary and return the num genes
    if person in one_gene:
        return 1
    elif person in two_genes:
        return 2
    return 0


def no_parents(num_genes, has_trait):
    """
    Returns the probability for person without parents.
    """
    # for anyone with no parents, use probability distribution PROBS["gene"] to determine
    # the probability that they have a particular number of the gene
    return PROBS["gene"][num_genes] * PROBS["trait"][num_genes][has_trait]


def has_parent(person, people, one_gene, two_genes):
    # for anyone with parents, each parent passes one of their two genes on to their child randomly
    # if the person has parents, identify the parents and check the number of genes of each parent
    mother = people[person]['mother']
    mother_genes = check_genes(mother, one_gene, two_genes)
    father = people[person]['father']
    father_genes = check_genes(father, one_gene, two_genes)

    # after checking the number of genes the parent has, divide by 2 to get half the value
    # bc, parent will pass one of their two genes (if they have any) on to their child
    pass_gene_mom = mother_genes/2
    pass_gene_dad = father_genes/2

    # there is a PROBS["mutation"] chance that it mutates (goes from being the gene to not being the gene)
    # if dad passes and no mutation
    prob_dad_pass_no_mutate = pass_gene_dad*(1 - PROBS["mutation"])
    # if dad passes and yes mutation
    prob_dad_pass_yes_mutate = pass_gene_dad*PROBS["mutation"]
    # if dad does not pass gene and no mutation
    prob_dad_no_pass_no_mutate = (1 - pass_gene_dad)*(1 - PROBS["mutation"])
    # if dad does not pass gene and yes mutation
    prob_dad_no_pass_yes_mutate = (1 - pass_gene_dad)*PROBS["mutation"]

    prob_mom_pass_no_mutate = pass_gene_mom*(1 - PROBS["mutation"])
    prob_mom_pass_yes_mutate = pass_gene_mom*PROBS["mutation"]
    prob_mom_no_pass_no_mutate = (1 - pass_gene_mom)*(1 - PROBS["mutation"])
    prob_mom_no_pass_yes_mutate = (1 - pass_gene_mom)*PROBS["mutation"]

    # check the number of genes of child and proceed with calculating the probability
    kid_genes = check_genes(person, one_gene, two_genes)

    # if the child has zero genes from parents (check cases of when mutation happens when both parents pass gene and so on)
    if kid_genes == 0:
        probability = (prob_dad_pass_yes_mutate*prob_mom_no_pass_no_mutate)+(prob_dad_pass_yes_mutate*prob_mom_pass_yes_mutate) + \
            (prob_mom_pass_yes_mutate*prob_dad_no_pass_no_mutate) + \
            (prob_dad_no_pass_no_mutate*prob_mom_no_pass_no_mutate)
    # if the child has 1 gene from parents (check cases of when mutation happens when one of the parents pass gene and other parent passes gene without mutation and so on)
    elif kid_genes == 1:
        probability = (prob_dad_pass_yes_mutate*prob_mom_pass_no_mutate)+(prob_dad_pass_no_mutate*prob_mom_pass_yes_mutate) + \
            (prob_dad_pass_no_mutate*prob_mom_no_pass_no_mutate)+(prob_dad_no_pass_no_mutate*prob_mom_pass_no_mutate) + \
            (prob_dad_pass_yes_mutate*prob_mom_no_pass_yes_mutate)+(prob_dad_no_pass_yes_mutate*prob_mom_pass_yes_mutate) + \
            (prob_dad_no_pass_no_mutate*prob_mom_no_pass_yes_mutate) + \
            (prob_dad_no_pass_yes_mutate*prob_mom_no_pass_no_mutate)
    # if the child has 2 genes from parents (check cases of when no mutation happens and both pass genes or mutation happens with both do not pass gene)
    elif kid_genes == 2:
        probability = (prob_dad_no_pass_yes_mutate*prob_mom_no_pass_yes_mutate)+(prob_dad_pass_no_mutate*prob_mom_pass_no_mutate) + \
            (prob_dad_no_pass_yes_mutate*prob_mom_pass_no_mutate) + \
            (prob_dad_pass_no_mutate*prob_mom_no_pass_yes_mutate)
    # return this probability
    return probability


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    # start with a probability of 1
    probability = 1
    # iterate through people dictionary and find out about the num copy of genes they have and whether they have listed trait or not
    for person in people:
        num_genes = check_genes(person, one_gene, two_genes)
        if person in have_trait:
            hasTrait = True
        else:
            hasTrait = False

        # check whether the person has parents or not, to determine whether to use no_parents() or has_parents() function
        if people[person]['mother'] == None:
            probability *= no_parents(num_genes, hasTrait)
        else:
            # make sure to multiply the probability returned from 'has_parent()' by the probability based on genes and trait
            probability *= (has_parent(person, people, one_gene, two_genes)) * \
                PROBS["trait"][num_genes][hasTrait]
    return probability


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    # for each person in probabilities, the function updates the probabilities[person]["gene"] distribution
    # and the probabilities[person]["trait"] distributiono by adding p to the appropriate value in each distribution
    for person in probabilities:
        # for this, you would have to check the number of genes the person has as well as whether they have the trait or not
        num_genes = check_genes(person, one_gene, two_genes)
        if person in have_trait:
            hasTrait = True
        else:
            hasTrait = False

        probabilities[person]["gene"][num_genes] += p
        probabilities[person]["trait"][hasTrait] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    # probabilities is dict of people and each person is mapped to a gene and trait distribution
    for person in probabilities:
        # we need to normalize distribution so that values in the distribution sum to 1
        # probability distribution sum of genes
        prob_genes = sum(probabilities[person]["gene"].values())
        # probability distribution sum of traits
        prob_traits = sum(probabilities[person]["trait"].values())

        # so for each gene (num of genes - 0, 1, 2) in the probability distribution
        for gene in probabilities[person]["gene"]:
            # the actual value given the gene (zero genes, one gene, two genes)
            actual_val = probabilities[person]["gene"][gene]
            # the normalized value will equal original value over sum of probability distribution of genes
            new_val = actual_val/prob_genes
            probabilities[person]["gene"][gene] = new_val

        # so for each trait (have trait or not) in the probability distribution
        for trait in probabilities[person]["trait"]:
            # the actual value given the trait (has trait or no trait)
            actual_val = probabilities[person]["trait"][trait]
            # the normalized value will equal original value over sum of probability distribution of traits
            new_val = actual_val/prob_traits
            probabilities[person]["trait"][trait] = new_val


if __name__ == "__main__":
    main()
