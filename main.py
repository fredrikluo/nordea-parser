"""This script reads a csv file and prints the amount and comment of each row"""

import argparse
from decimal import Decimal
import pandas as pd
import dateparser


def parse_amount(line: str):
    """
    Parse the last “XX XXX,YY” amount in line without regex.
    Returns (integer_part: str, decimal_part: str), e.g. ("26038", "68").
    """
    stack = []
    groups = []
    decimal = ""
    sign = ""
    has_space = False
    parse_done = False

    # a small stack based parser for the amount in a line
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
                parse_done = True
                break
        elif ch == " ":
            if len(stack) == 3:
                groups.append("".join(reversed(stack)))
                stack.clear()
            elif 0 < len(stack) < 3:
                groups.append("".join(reversed(stack)))
                stack.clear()
                parse_done = True
                break
            elif len(stack) > 3:
                if not has_space:
                    # we discovered that the number doesn't use space
                    # as a separator, so we are done
                    groups.append("".join(reversed(stack)))
                    stack.clear()
                parse_done = True
                break

            has_space = True
        else:
            break

    if not parse_done and len(stack) > 0:
        # if we have a stack left, it means we have a number
        groups.append("".join(reversed(stack)))
        stack.clear()

    integer = sign + "".join(reversed(groups))
    full_number = sign + " ".join(reversed(groups)) + ("," + decimal if decimal else "")
    idx = line.rfind(full_number)
    return f"{integer}.{decimal}", idx


def parse_date_description(line: str):
    """
    Parse the date and description from a line.
    Returns (date: str, description: str).
    """
    parts = line.split(" ")
    dt = dateparser.parse(" ".join(parts[0:3]), languages=["nb"])
    description = " ".join(parts[3:]).strip()
    return dt, description


def parse_payment_line(line):
    """Parse a single line of credit card record and return the amount and description"""
    amount, idx = parse_amount(line)
    date, description = parse_date_description(line[:idx].strip())
    return date, description, Decimal(amount)


def parse_creditcard_records(creditcard_record_filename):
    """Parse a credit card record file and return a list of transactions"""
    with open(creditcard_record_filename, "r", encoding="utf-8") as f:
        lines = list(filter(lambda x: x.strip() != "", f.readlines()))
        for line in lines:
            date, description, amount = parse_payment_line(line)
            yield date, amount, description


def parse_debitcard(csvfilename: str):
    """Main function that reads a csv file and prints the amount and comment of each row"""
    # parse the csvfile into dataframe
    df = pd.read_csv(csvfilename, sep=";")

    # go through it row by row
    for _, row in df.iterrows():
        amount = Decimal(row["Beløp"].replace(",", "."))
        description = row["Tittel"]
        date = dateparser.parse(row["Bokføringsdato"], languages=["nb"])
        if date is None:
            continue

        yield date, amount, description


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Add arguments
    parser.add_argument("csvfilename", type=str, help="csv filename")
    parser.add_argument(
        "creditcard_record_filename", type=str, help="credit card record filename"
    )
    args = parser.parse_args()
    result = list(parse_debitcard(args.csvfilename))
    result += list(parse_creditcard_records(args.creditcard_record_filename))

    for _date, _amount, _description in result:
        print(f"{_date};{_amount};{_description}")
