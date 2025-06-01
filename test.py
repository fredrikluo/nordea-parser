from main import parse_amount, parse_date_description

if __name__ == "__main__":
    line = "29 mai 2025 7ELEVEN7 067 FrNansen 121 -49,00"
    amount, idx = parse_amount(line)
    date, description = parse_date_description(line[:idx].strip())
    print(f"Amount: {amount}, Date: {date}, Description: {description}")