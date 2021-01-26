import argparse
from dirtyfast import smms_upload, rounded_corners, create_random_file
import dirtyfast as df


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d",
                        "--ddfile",
                        type=int,
                        help="Create a file with os.urandom.")
    parser.add_argument("-sm",
                        "--smms",
                        type=str,
                        help="Upload image to sm.ms")
    parser.add_argument("-rc",
                        "--roundcorner",
                        nargs='*',
                        metavar=('test.png', 20),
                        help="Add rounded corners to images.")
    parser.add_argument("-ip", "--ip", action='store_true', help="Curl cip.cc")
    
    args = parser.parse_args()
    if args.ddfile:
        create_random_file(int(args.ddfile))
    elif args.smms:
        smms_upload(args.smms)
    elif args.roundcorner:
        image_path = args.roundcorner[0]
        radius = 20 if len(args.roundcorner) == 1 else int(args.roundcorner[1])
        rounded_corners(image_path, radius)
    elif args.ip:
        df.p(df.shell("curl -s cip.cc"))
