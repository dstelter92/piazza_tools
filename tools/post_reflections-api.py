#!/usr/bin/python2

import sys, time, argparse
import getpass
from piazza_api import Piazza
import piazza_api.exceptions

DEBUG = 0

### Checks all posts that match query for participation. Counts which students
### have responded for each post.

## Command line args
parser = argparse.ArgumentParser(description='Search for posts and find'
        ' students that participated on that group of posts')
parser.add_argument('-c', '--classid', metavar='classID', type=str, nargs='?',
        help='Piazza classID from URL')
parser.add_argument('-e', '--email', metavar='email', type=str, nargs='?',
        help='Piazza email to login with')
parser.add_argument('-t', '--title', metavar='title', type=str, nargs='*',
        help='Title of post, gets appended with discussion section')
parser.add_argument('-n', '--nsects', metavar='nsects', type=int,
        help='Number of discussion sections')
parser.add_argument('-s', '--status', metavar='status', type=str, nargs='?',
        help='Activity of posts (active, private)')


args = parser.parse_args()
classid = args.classid
email = args.email
title = ' '.join(args.title)
nsects = args.nsects
active = args.status

content = "What chemistry topics were new to you this past week? What was"\
        "confusing?\n\n Many students have the same confusions, so take a "\
        "look at what your peers have answered. See something you understand"\
        "that they don't? Start a discussion! See something you are also "\
        "confused about? Tell them why!\n\n Post your response in this thread"\
        " before Tuesday's lecture.\n\n "

print 'Connecting to Piazza via piazza-api...'

# Piazza setup
p = Piazza()
p.user_login(email=email,password=None)
me = p.get_user_profile()
pclass = p.network(classid)
print '  Logged in as:', me.get('name')
print ''

for i in range(nsects):
    disc = 'B ' + str(i+1)
    thistitle = '{} B{}'.format(title, i+1)
    params = {
        'status': active,
        'type': 'note',
        'folders': [disc],
        'subject': thistitle,
        'content': content,
        'config': {'feed_groups': disc.lower() + '_' + classid}
        }
    try:
        pclass._rpc.content_create(params)
    except piazza_api.exceptions.RequestError:
        print 'Could not post, ignoring'
        continue
    finally:
        time.sleep(5)

    print 'Added post with title:',thistitle



sys.exit()
