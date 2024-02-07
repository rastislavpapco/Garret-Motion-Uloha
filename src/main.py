import argparse
import pandas as pd

from calculator import Calculator


def main():
    # Load config and input data
    calculator = Calculator(args.config_file)
    with open(args.data_file, 'r') as f:
        data = f.read()

    # Calculate costs
    costs = calculator.calculate(data)

    # Save calculated costs to csv
    df = pd.read_csv(args.data_file, header=None, names=["phone_number", "call_start", "call_end"])
    df['costs'] = costs
    df.to_csv("data/calculated_costs.csv", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("data_file", help="Path to csv data file.")
    parser.add_argument("config_file", help="Path to config file.")
    args = parser.parse_args()
    main()
