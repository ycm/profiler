#!/usr/bin/env python3

# generate_performance_score_profile.py
# Generate score profiles for readings in a directory, based on 'gold' readings

import os
import argparse
import pandas as pd

def generate_scores_for_session():
    pass

def main():
    parser = argparse.ArgumentParser(description="Generate score profiles for readings in a directory, based on 'gold' readings")
    parser.add_argument('to_evaluate_dir', type=str, help='Directory with readings to evaluate')
    parser.add_argument('gold_readings_dir', type=str, help='Directory with gold readings')
    args = parser.parse_args()
    to_evaluate_dir = args.to_evaluate_dir
    gold_readings_dir = args.gold_readings_dir    

    gold_readings_dataframes = [
        pd.read_csv(os.path.join(gold_readings_dir, file), sep='\t').fillna('').rename(columns={'Unnamed: 0': 'gold_token'})
        for file in os.listdir(gold_readings_dir)
    ]


if __name__ == "__main__":
    main()