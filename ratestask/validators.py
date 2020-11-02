from datetime import datetime
import argparse


def valid_date(s):
    try:
        return datetime.strptime(str(s), "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


def valid_currency(s):
    if len(s) == 3:
        return s
    else:
        raise argparse.ArgumentTypeError("String must be 3 characters long")
