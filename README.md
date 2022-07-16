# A Reddit downloader

## Usage:
redDownIt allows you to download images and (some) gif from Reddit.com of a subreddit or user.
Simply download the data that reddit provide us with their JSON (hot.json/top.json/new.json)

For each subreddit/user you can pick the mode like "top" or "new", you can also create a preferences file to store subreddit-mode and user-mode.. At the start you can choose if you want to load/create a JSON or just download files.

- The file preferences should be in the same folder of the program
- The data will be downloaded in the "./dwn/" folder

`$ python3 redDownIt.py`

**Don't need for reddit's account**

## Dependencies:
- requests
- bs4
- os
- PIL (//pip3 install Pillow)
- hashlib

> installable with pip3

## Output be like
![output](https://github.com/albertomorini/albertomorini/blob/main/redditDownloader/imgExample/output.png)


<a href="https://github.com/albertomorini/albertomorini/blob/main/redditDownloader/imgExample/proofOfWork.png">Proof of work</a>

## TODO:
- [ ] make a GUI
- [X] create folder "dwn" if doesn't exists
- [X] import JSON prefereces
- [ ] download video
- [ ] download album of images
- [ ] search user/subreddit
