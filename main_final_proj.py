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

    # print the number of rows and columns
    print(occurence_df.shape)
    # print the first 5 rows, ignore width limitation
    print(occurence_df.head())
    # print all the columns
    print(occurence_df.columns.tolist())

    # print the max_ma, min_ma, early_interval, late_interval
    print(occurence_df['max_ma'].head())
    print(occurence_df['min_ma'].head())
    print(occurence_df['early_interval'].head())
    print(occurence_df['late_interval'].head())
    # print the phylum, class, order, family, genus, primary_name
    print(occurence_df['phylum'].head())
    print(occurence_df['class'].head())
    print(occurence_df['order'].head())
    print(occurence_df['family'].head())
    print(occurence_df['genus'].head())

    # read in the occurence_all_cont_ident.csv file
    pbdb_df = pd.read_csv('occurence_all_cont_ident.csv', skiprows=18)
    # print the first 5 rows
    print(pbdb_df.head())
    # print the columns
    print(pbdb_df.columns.tolist())
    # print the shape
    print(pbdb_df.shape)

    # join the two dataframes on the occurrence_no, drop the entries with no match in occurence_df
    # only need 'reference_no', 'primary_name', 'primary_reso', 'subgenus_name', 'subgenus_reso', 'species_name', 'species_reso' from pbdb_df
    pbdb_df = pbdb_df[['occurrence_no', 'reference_no', 'primary_name', 'primary_reso', 'subgenus_name', 'subgenus_reso', 'species_name', 'species_reso']]
    # join the two dataframes on the occurrence_no, drop the entries with no match in occurence_df
    occurence_df = occurence_df.merge(pbdb_df, on='occurrence_no', how='inner')
    # print the shape
    print(occurence_df.shape)
    # print the first 5 rows
    print(occurence_df.head())
    # print the columns
    print(occurence_df.columns.tolist())

    # save the max_ma, min_ma, early_interval, late_interval,
    # phylum, class, order, family, genus, primary_name, species_name to a csv file
    occurence_df[['max_ma', 'min_ma', 'early_interval', 'late_interval',
                     'phylum', 'class', 'order', 'family', 'genus', 'primary_name']].to_csv('interval_taxonomic_data.csv', index=False)
