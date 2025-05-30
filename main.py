"""This script reads a csv file and prints the amount and comment of each row"""

import argparse
from decimal import Decimal
import pandas as pd


def parse_amount(line: str):
    """
    Parse the last “XX XXX,YY” amount in line without regex.
    Returns (integer_part: str, decimal_part: str), e.g. ("26038", "68").
    """
    stack = []
    groups = []
    decimal = ""
    sign = ""

    #a small stack based parser for the amount in a line
    for ch in reversed(line.strip()):
        if ch.isdigit():
            stack.append(ch)
        elif ch == ",":
            decimal = "".join(reversed(stack))
            stack.clear()
        elif ch == "-":
            if len(stack) <= 3:
                groups.append("".join(reversed(stack)))
                stack.clear()
                sign = "-"
                break
        elif ch == " ":
            if len(stack) == 3:
                groups.append("".join(reversed(stack)))
                stack.clear()
            elif 0 < len(stack) < 3:
                groups.append("".join(reversed(stack)))
                stack.clear()
                break
        else:
            break

    integer = sign + "".join(reversed(groups))
    full_number = integer + ("," + decimal if decimal else "")
    idx = line.replace(" ", "").rfind(full_number)
    return f"{integer}.{decimal}", idx


def parse_creditcard_records(creditcard_record_filename):
    """Parse a credit card record file and return a list of transactions"""
    with open(creditcard_record_filename, "r", encoding="utf-8") as f:
        lines = list(filter(lambda x: x.strip() != "", f.readlines()))
        for line in lines:
            _, description, amount = parse_payment_line(line)
            print(f"{amount};{description}")


def parse_payment_line(line):
    """Parse a single line of credit card record and return the amount and description"""
    amount, idx = parse_amount(line)
    return "", line[:idx].strip(), Decimal(amount)


def parse_csv(csvfilename: str):
    """Main function that reads a csv file and prints the amount and comment of each row"""
    # parse the csvfile into dataframe
    df = pd.read_csv(csvfilename, sep=";")

    # go through it row by row
    for _, row in df.iterrows():
        amount = Decimal(row["Beløp"].replace(",", "."))
        comment = row["Tittel"]
        print(f"{amount};{comment}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Add arguments
    parser.add_argument("csvfilename", type=str, help="csv filename")
    parser.add_argument(
        "creditcard_record_filename", type=str, help="credit card record filename"
    )
    args = parser.parse_args()
    parse_csv(args.csvfilename)
    parse_creditcard_records(args.creditcard_record_filename)
