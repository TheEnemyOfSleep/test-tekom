from datetime import datetime
import requests
import time
import sys
import argparse
import logging

from requests import exceptions


parser = argparse.ArgumentParser(description="Flip a switch by setting a flag")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-f', '--file', type=str, help='json or xml file with resourses')
group.add_argument('-d', '--data', nargs='+', help='list, tuple, dict data with resourses')


def main(resourse):
    if isinstance(resourse, str):
        r = requests.get(resourse)
        print(str(r.status_code) + '\n')
        print(resourse)
    elif isinstance(resourse, list):
        for site in resourse:
            try:
                r = requests.get(site)
                print(str(r.status_code) + ' - ' + str(site))
            except requests.exceptions.ConnectionError:
                print('{} - refused request'.format(site))
            except requests.exceptions.HTTPError as err:
                print('url - {} does not connect'.format(site))


if __name__ == "__main__":
    args = parser.parse_args()
    if args.file:
        resourse = args.file
    else:
        resourse = args.data
    while True:
        try:
            time.sleep(1)
            main(resourse)
        except KeyboardInterrupt:
            sys.exit(0)