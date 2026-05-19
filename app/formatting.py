from datetime import datetime


def format_money(amount):
    value = int(round(float(amount or 0)))
    sign = "-" if value < 0 else ""
    digits = str(abs(value))

    if len(digits) <= 3:
        grouped = digits
    else:
        last_three = digits[-3:]
        leading = digits[:-3]
        groups = []
        while leading:
            groups.insert(0, leading[-2:])
            leading = leading[:-2]
        grouped = ",".join(groups + [last_three])

    return f"{sign}₹{grouped}"


def format_date(date_text):
    if not date_text:
        return "No date"

    try:
        parsed = datetime.fromisoformat(date_text)
    except ValueError:
        return str(date_text).split("T", 1)[0]

    return f"{parsed.day} {parsed:%b %Y}"
