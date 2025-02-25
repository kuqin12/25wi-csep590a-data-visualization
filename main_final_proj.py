import pandas as pd
import time
import random
import get_nba_data
import os


# Run the main function
if __name__ == "__main__":
    # load the data into a dataframe from the csv file
    # ignore the first 18 rows
    occurence_df = pd.read_csv('occurence_all_cont_all_out.csv', skiprows=18)

    print(occurence_df.head())
