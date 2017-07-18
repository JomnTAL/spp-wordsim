#!/usr/bin/env python


import argparse
import logging
import csv


def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('output_base')
    parser.add_argument('raw_input', nargs="+")
    parser.add_argument('-l', '--logger', default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="Logging level: DEBUG, INFO (default), WARNING, ERROR")
    args = parser.parse_args()

    numeric_level = getattr(logging, args.logger.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: {}".format(args.logger))
    logging.basicConfig(level=numeric_level)

    return args


def main():
    args = argparser()

    pairs = set()

    with open(args.output_base + "200ms.csv", 'w') as fout200, open(args.output_base + "1200ms.csv", 'w') as fout1200:
        print("target,prime,rt", file=fout200)
        print("target,prime,rt", file=fout1200)
        for raw in args.raw_input:
            with open(raw, 'r') as fin:
                csv_raw = csv.DictReader(fin)
                header = csv_raw.fieldnames
                if "LDT 200ms RT" in header:
                    rt_name = "LDT"
                else:
                    rt_name = "NT"
                for line in csv_raw:
                    rt200 = rt_name + " 200ms RT"
                    rt1200 = rt_name + " 1200ms RT"
                    target = line["TargetWord"]
                    prime = line["Prime"] if "Prime" in header else line["Unrelated"]
                    if (target, prime) in pairs:
                        continue
                    pairs.add((target, prime))
                    print("{},{},{}".format(target, prime, line[rt200]),
                          file=fout200)
                    print("{},{},{}".format(target, prime, line[rt1200]),
                          file=fout1200)


if __name__ == '__main__':
    main()
