import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """

    # list which specifies the type of each column (1 - integer, 2 - floats, 3 - month, 4 - label)
    column_types = [
        1, 2, 1, 2, 1, 2, 2, 2, 2, 2, 3, 1, 1, 1, 1, 4, 4
    ]
    month = {
        "Jan": 0,
        "Feb": 1,
        "Mar": 2,
        "Apr": 3,
        "May": 4,
        "June": 5,
        "Jul": 6,
        "Aug": 7,
        "Sep": 8,
        "Oct": 9,
        "Nov": 10,
        "Dec": 11
    }

    # store evidences of first 16 columns
    evidences = []
    # store label (last column)
    labels = []
    with open(filename) as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            evidence = []
            for i in range(16):
                # based on the category, add item as the correct type into evidence list
                if column_types[i] == 1:
                    evidence.append(int(row[i]))
                elif column_types[i] == 2:
                    evidence.append(float(row[i]))
                elif column_types[i] == 3:
                    evidence.append(month[row[i]])
                elif column_types[i] == 4:
                    if row[i] == "TRUE" or row[i] == "Returning_Visitor":
                        evidence.append(1)
                    else:
                        evidence.append(0)

            evidences.append(evidence)
            # for label (last column), add separately to labels list
            label = 1 if row[17] else 0
            labels.append(label)
    return evidences, labels


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    # given the evidence and labels list from data (csv),
    # use the KNeighborsClassifier to create a model
    model = KNeighborsClassifier(n_neighbors=1)
    # fitted model which is trained on the data
    model.fit(evidence, labels)
    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    # the number of entries of data set
    total_size = len(labels)
    # the actual number of positives in dataset
    total_positives = 0
    # the actual number of negatives in dataset
    total_negatives = 0
    # the number of positives that were predicted correctly
    correctly_predicted_positives = 0
    # the number of negatives that were predicted correctly
    correctly_predicted_negatives = 0

    for i in range(total_size):
        # if label from original dataset is positive
        if labels[i] == 1:
            total_positives += 1
            if labels[i] == predictions[i]:
                # increment value if the label and predicted value are same
                correctly_predicted_positives += 1
        # if label from original dataset is negative
        elif labels[i] == 0:
            total_negatives += 1
            if labels[i] == predictions[i]:
                # increment value if the label and predicted value are same
                correctly_predicted_negatives += 1

    sensitivity = correctly_predicted_positives/total_positives
    
    specificity = correctly_predicted_negatives/total_negatives

    return sensitivity, specificity


if __name__ == "__main__":
    main()
