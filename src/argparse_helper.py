import argparse
import dofast as df


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
    parser.add_argument("-gu",
                        "--githupupload",
                        help="Upload files to Github/drocat/stuff")

    args = parser.parse_args()
    if args.ddfile:
        df.create_random_file(int(args.ddfile))
    elif args.smms:
        df.smms_upload(args.smms)
    elif args.githupupload:
        df.githup_upload(args.githupupload)
    elif args.roundcorner:
        image_path = args.roundcorner[0]
        radius = 20 if len(args.roundcorner) == 1 else int(args.roundcorner[1])
        df.rounded_corners(image_path, radius)
    elif args.ip:
        df.p(df.shell("curl -s cip.cc"))
