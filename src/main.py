import argparse
from VideoCutter import VideoCutter


def main():
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="This program cuts a given video at the timestamps with the word 'cut'.",
        epilog="Example usage: main.py recordings/video.mp4 --output_folder_path recordings/clips",
    )
    parser.add_argument("video_path", help="The path of the input video.")
    parser.add_argument(
        "--output_folder_path",
        help="The folder path of the output videos. If left blank, it will default to the same sirectory as the input video path.",
    )
    args = parser.parse_args()
    VideoCutter().cut_video_recognize(args.video_path, args.output_folder_path)


if __name__ == "__main__":
    main()
