#!/usr/bin/python2

import sys, time, argparse
import getpass
from piazza_api import Piazza
import piazza_api.exceptions

### Posts a reflection thread for each group on piazza

## Command line args
parser = argparse.ArgumentParser(description='Post reflections thread'
        ' for each nsect groups in piazza')
parser.add_argument('-c', '--classid', metavar='classID', type=str, nargs='?',
        help='Piazza classID from URL')
parser.add_argument('-e', '--email', metavar='email', type=str, nargs='?',
        help='Piazza email to login with')
parser.add_argument('-t', '--title', metavar='title', type=str, nargs='*',
        help='Title of post, gets appended with discussion section')
parser.add_argument('-n', '--ngroups', metavar='ngroups', type=int,
        help='Number of discussion sections', default=1)
parser.add_argument('-s', '--status', metavar='status', type=str, nargs='?',
        help='Activity of posts (active, private)', default='active')
parser.add_argument('-g', '--groupname', metavar='groupname', type=str, nargs='?',
        help='Basename of each group', default='')


args = parser.parse_args()
classid = args.classid
email = args.email
title = ' '.join(args.title)
nsects = args.ngroups
active = args.status
groupname = args.groupname

content = "What chemistry topics were new to you this past week? What was "\
        "confusing?\n\n Many students have the same confusions, so take a "\
        "look at what your peers have answered. See something you understand "\
        "that they don't? Start a discussion! See something you are also "\
        "confused about? Tell them why!\n\n Post your response in this thread"\
        " before Tuesday's lecture.\n\n #pin"

print('Connecting to Piazza via piazza-api...')

# Piazza setup
p = Piazza()
p.user_login(email=email,password=None)
me = p.get_user_profile()
pclass = p.network(classid)
print('  Logged in as: %s' % me.get('name'))
print('')

for i in range(nsects):
    if (groupname != ''):
        thistitle = '{} {}{}'.format(title,groupname,i+1)
        disc = groupname + ' ' + str(i+1)
        params = {
            'status': active,
            'type': 'note',
            'folders': [disc],
            'subject': thistitle,
            'content': content,
            'config': {'feed_groups': disc.lower() + '_' + classid}
        }
    else:
        thistitle = title
        params = {
            'status': active,
            'type': 'note',
            'subject': title,
            'content': content,
        }

    try:
        pclass._rpc.content_create(params)
    except piazza_api.exceptions.RequestError:
        print('Could not post, ignoring')
        continue
    finally:
        time.sleep(5) # don't overload piazza servers

    print('Added post with title: %s' % thistitle)



sys.exit()
