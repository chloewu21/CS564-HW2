
"""
FILE: skeleton_parser.py
------------------
Author: Firas Abuzaid (fabuzaid@stanford.edu)
Author: Perth Charernwattanagul (puch@stanford.edu)
Modified: 04/21/2014

Skeleton parser for CS564 programming project 1. Has useful imports and
functions for parsing, including:

1) Directory handling -- the parser takes a list of eBay json files
and opens each file inside of a loop. You just need to fill in the rest.
2) Dollar value conversions -- the json files store dollar value amounts in
a string like $3,453.23 -- we provide a function to convert it to a string
like XXXXX.xx.
3) Date/time conversions -- the json files store dates/ times in the form
Mon-DD-YY HH:MM:SS -- we wrote a function (transformDttm) that converts to the
for YYYY-MM-DD HH:MM:SS, which will sort chronologically in SQL.

Your job is to implement the parseJson function, which is invoked on each file by
the main function. We create the initial Python dictionary object of items for
you; the rest is up to you!
Happy parsing!
"""

import sys
from json import loads
from re import sub

columnSeparator = "|"

# Dictionary of months used for date transformation
MONTHS = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06',\
        'Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}

"""
Returns true if a file ends in .json
"""
def isJson(f):
    return len(f) > 5 and f[-5:] == '.json'

"""
Converts month to a number, e.g. 'Dec' to '12'
"""
def transformMonth(mon):
    if mon in MONTHS:
        return MONTHS[mon]
    else:
        return mon

"""
Transforms a timestamp from Mon-DD-YY HH:MM:SS to YYYY-MM-DD HH:MM:SS
"""
def transformDttm(dttm):
    dttm = dttm.strip().split(' ')
    dt = dttm[0].split('-')
    date = '20' + dt[2] + '-'
    date += transformMonth(dt[0]) + '-' + dt[1]
    return date + ' ' + dttm[1]

"""
Transform a dollar value amount from a string like $3,453.23 to XXXXX.xx
"""

def transformDollar(money):
    if money == None or len(money) == 0:
        return money
    return sub(r'[^\d.]', '', money)

"""
Parses a single json file. Currently, there's a loop that iterates over each
item in the data set. Your job is to extend this functionality to create all
of the necessary SQL tables for your database.
"""
def parseJson(json_file):
    if not hasattr(parseJson, 'seen_users'):
        parseJson.seen_users = set()
    seen_users = parseJson.seen_users # keep track of users we have already seen

    if not hasattr(parseJson, 'seen_categories'):
        parseJson.seen_categories = set()
    seen_categories = parseJson.seen_categories

    if not hasattr(parseJson, 'seen_item_categories'):
        parseJson.seen_item_categories = set()
    seen_item_categories = parseJson.seen_item_categories

    if not hasattr(parseJson, 'next_bid_id'):
        parseJson.next_bid_id = 1

    def formatText(value):
        if value is None:
            return 'NULL'
        return '"' + value.replace('"', '""') + '"'

    with open(json_file, 'r') as f:
        items = loads(f.read())['Items'] # creates a Python dictionary of Items for the supplied json file
        items_file = open("items.dat", "a")
        users_file = open("users.dat", "a")
        bids_file = open("bids.dat", "a")
        categories_file = open("categories.dat", "a")
        item_categories_file = open("item_categories.dat", "a")

        for item in items:
            """
            TODO: traverse the items dictionary to extract information from the
            given `json_file' and generate the necessary .dat files to generate
            the SQL tables based on your relation design
            """
            # users (sellers)
            if item['Seller']['UserID'] not in seen_users:
                row = formatText(item['Seller']['UserID'])
                row += columnSeparator + str(item['Seller']['Rating'])
                row += columnSeparator + formatText(item['Location'])
                row += columnSeparator + formatText(item['Country'])
                users_file.write(row + '\n')
                seen_users.add(item['Seller']['UserID'])
            
            # items
            item_row = str(item['ItemID'])
            item_row += columnSeparator + formatText(item['Seller']['UserID'])
            item_row += columnSeparator + formatText(item['Name'])
            item_row += columnSeparator + transformDollar(item['Currently'])
            buy_price = transformDollar(item.get('Buy_Price'))
            item_row += columnSeparator + (buy_price if buy_price is not None else 'NULL')
            item_row += columnSeparator + transformDollar(item['First_Bid'])
            item_row += columnSeparator + str(item['Number_of_Bids'])
            item_row += columnSeparator + formatText(transformDttm(item['Started']))
            item_row += columnSeparator + formatText(transformDttm(item['Ends']))
            item_row += columnSeparator + formatText(item.get('Description'))
            items_file.write(item_row + '\n')

            # categories and item_categories
            for category in item['Category']:
                if category not in seen_categories:
                    categories_file.write(formatText(category) + '\n')
                    seen_categories.add(category)

                item_category = (item['ItemID'], category)
                if item_category not in seen_item_categories:
                    row = str(item['ItemID'])
                    row += columnSeparator + formatText(category)
                    item_categories_file.write(row + '\n')
                    seen_item_categories.add(item_category)

            # bids and users(bidders)
            for wrapped_bid in item['Bids'] or []:
                bid = wrapped_bid['Bid']
                bidder = bid['Bidder']

                if bidder['UserID'] not in seen_users:
                    row = formatText(bidder['UserID'])
                    row += columnSeparator + str(bidder['Rating'])
                    row += columnSeparator + formatText(bidder.get('Location'))
                    row += columnSeparator + formatText(bidder.get('Country'))
                    users_file.write(row + '\n')
                    seen_users.add(bidder['UserID'])

                bid_row = str(parseJson.next_bid_id)
                bid_row += columnSeparator + str(item['ItemID'])
                bid_row += columnSeparator + formatText(bidder['UserID'])
                bid_row += columnSeparator + formatText(transformDttm(bid['Time']))
                bid_row += columnSeparator + transformDollar(bid['Amount'])
                bids_file.write(bid_row + '\n')
                parseJson.next_bid_id += 1

        items_file.close()
        users_file.close()
        bids_file.close()
        categories_file.close()
        item_categories_file.close()

"""
Loops through each json files provided on the command line and passes each file
to the parser
"""
def main(argv):
    if len(argv) < 2:
        print('Usage: python skeleton_json_parser.py <path to json files>', file=sys.stderr)
        sys.exit(1)

    # loops over all .json files in the argument
    for f in argv[1:]:
        if isJson(f):
            parseJson(f)
            print ("Success parsing " + f)

if __name__ == '__main__':
    main(sys.argv)
