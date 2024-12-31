# Speech Recognition Video Cutter

## Overview

This Python program cuts a given video at the timestamps with the word 'cut'.

## Why I made this

I made this during the 2024 semester break because I was bored. Also, I wanted to finally make a personal project.

## Usage

### Initiation

```sh
conda env create -f ./environment.yml --prefix ./env
conda activate ./env
pip install -r ./requirements.txt
```

### Running the CLI

```sh
main.py path/to/video.mp4 --output_folder_path path/to/output/folder
```
