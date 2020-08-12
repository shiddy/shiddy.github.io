#!/usr/bin/env python3
import sys
import os

# We are provided the directory of the outputted files
# I want to go through the posts and
# * replace the {{CREATED=DATE}}
# * generate an archive link with the CREATED DATE


dest_dir = sys.argv[-1]
post_dir = f"{dest_dir}/posts"

post_paths = [os.path.join(post_dir, f) for f in list(os.walk(post_dir))[0][2]]

for post in post_paths:
    with open(post, 'r') as f:
        # The Meta tags should be somewhere in the first 10 lines of the file
        head = [next(f) for x in range(10)]
    print(head)
# print(os.getenv('urls'))
# print(os.getenv('src'))
# print("@@@@@@@@@@@@@@@")

