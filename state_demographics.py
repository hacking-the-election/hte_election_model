import pandas as pd 
import numpy as np
from math import exp

def calculate_sss(write=False):
    """
    Calculates state similarity scores based on different metrics in data.
    Parameters:
        write - If True, writes to "state_similarities.csv", else returns
            DataFrame of scores for each matchup. Defaults to False.
    """
    # Vectorize the exp function
    normalize = np.vectorize(exp)
    # Read from data and split into raw data and Similarities.
    df = pd.read_csv("data/Daily Kos Elections State Similarity Index - Similarity.csv")
    similarity_mask = df.columns.str.endswith("Similarity")
    raw = df[df.columns[~similarity_mask]].T
    # Insert congressional districts for states that split electoral votes-
    # assumes states have exactly the same parameters as states, which is obviously not true
    # but has to be used absent other data. To differentiate, the cook pvi accounts for partisanship.
    raw.insert(21, "Maine-2", np.append(np.array(["Maine-2"]),raw.iloc[1:,20]), allow_duplicates=True)
    raw.insert(21, "Maine-1", np.append(np.array(["Maine-1"]),raw.iloc[1:,20]), allow_duplicates=True)
    raw.insert(31, "Nebraska-3", np.append(np.array(["Nebraska-3"]),raw.iloc[1:,20]), allow_duplicates=True)
    raw.insert(31, "Nebraska-2", np.append(np.array(["Nebraska-2"]),raw.iloc[1:,20]), allow_duplicates=True)
    raw.insert(31, "Nebraska-1", np.append(np.array(["Nebraska-1"]),raw.iloc[1:,20]), allow_duplicates=True)
    raw = raw.T.reset_index().drop("index", axis=1)
    # Set "average" score array up
    average = np.zeros((57,57))
    # Iterate through columns of data
    for _, array in raw.iloc[:, 1:].iteritems():
        # Convert array if in string format
        try:
            array = array.astype(float)
        except ValueError:
            array = (array.str[1:-4] + array.str[-3:]).astype(int)
        # Create list of every possible matchup, calculate difference vectorwise
        x, y = np.meshgrid(array, array)
        difference = np.where(array[0] < 100, x-y, 100*np.where(x > y, 1-y/x, 1-x/y))
        # Find standard deviation and use that to normalize scores to 0-1.
        std = difference[0].std()
        score = normalize((-((difference/100)**2))/((2*std/100)**2))
        # Add the score array to our average array
        average += score
    # Actually divide by the number of data columns
    average = pd.DataFrame(average/(len(raw.columns)-1))
    # Set rows and columns to original states/US and DC
    average.index = raw.iloc[:, 0]
    average.columns = raw.iloc[:, 0]
    # Write rounded scores to file as csv
    with open("data/state_similarities.csv", "w") as f:
        f.write(pd.DataFrame(np.around(average, 3)).to_csv())

if __name__ == "__main__":
    calculate_sss(write=True)