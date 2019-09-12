#!/usr/bin/python2

import sys, argparse
import getpass, re, datetime
from piazza_api import Piazza

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
parser.add_argument('-q', '--query', metavar='query', type=str, nargs='*',
        help='Search query')
parser.add_argument('-s', '--skip', metavar='skip', type=str, nargs='*',
        help='Skip post type (question / poll / note)')
parser.add_argument('-d', '--duedate', metavar='duedate', type=str, nargs='*',
        help='Weekly due date for posts, format: DDD-HH:MM' +
            'example: TUE-17:00')

args = parser.parse_args()
classid = args.classid
email = args.email
query = ' '.join(args.query)
skip = args.skip
duedate = args.duedate

if (duedate):
    duedate = ''.join(duedate)
    r = re.compile('...-..:..')
    if not r.match(duedate):
        print('Invalid Due Date: %s' % duedate)
        sys.exit()
    duedate = duedate.split('-')
    duetime = list(map(int, duedate[1].split(':')))
    if (duedate[0] == 'MON'):
        day = 0
    elif (duedate[0] == 'TUE'):
        day = 1
    elif (duedate[0] == 'WED'):
        day = 2
    elif (duedate[0] == 'THU'):
        day = 3
    elif (duedate[0] == 'FRI'):
        day = 4
    elif (duedate[0] == 'SAT'):
        day = 5
    elif (duedate[0] == 'SUN'):
        day = 6
    else:
        day = -1
    if (day == -1):
        print('Invalid Due Day: %s' % duedate[0])
        sys.exit()


fname = 'query-%s_participation-%s.csv' % (query,classid)

print('Connecting to Piazza via piazza-api...')

# Piazza setup
p = Piazza()
p.user_login(email=email,password=None)
me = p.get_user_profile()
pclass = p.network(classid)
print('  Logged in as: %s' % me.get('name'))
print('')

# Get user list of name, email and piazza_id
print('Finding all students in Piazza class: %s' % classid)
users = pclass.get_all_users()
students = [] ## Contains all info about students
sdict = {} ## Dictionary lookup, UID -> email
profs = [] ## Contains all info about instructors
for user in users:
    # Get data from piazza API
    student_name = str(user.get('name'))
    student_email = str(user.get('email'))
    piazza_ID = str(user.get('id'))

    # Check to make sure they are a student
    role = user.get('role')
    if role != 'student':
        ## Debug check to print Prof/TA info
        print('--> IGNORE Prof/TA: %s id: %s' % (student_name,piazza_ID))
        profs.append(piazza_ID)
        continue

    # Put data into list/dict
    data = [student_name,student_email,piazza_ID]
    students.append(data)
    sdict[piazza_ID] = student_email
print('Found %d students' % len(students))
print('')


# Get poll posts
posts = pclass.search_feed(query)
print('Searching posts containing "%s"' % query)
post_names = []
nposts = 0
tviews = 0
for post in posts:
    # Get some info about the post
    post_cid = int(post.get('nr'))
    subject = str(post.get('subject'))
    views = int(post.get('unique_views'))
    this_post = pclass.get_post(post_cid)

    # Get date of post creation, find next 'date' day
    postcreated = this_post.get('created').split('T')
    if (duedate):
        postdate = list(map(int, postcreated[0].split('-')))
        postdate = datetime.datetime(postdate[0], postdate[1], postdate[2])
        print(postdate)
        offset = (day - postdate.weekday() + 7) % 7
        due = postdate + datetime.timedelta(days=offset, hours=duetime[0],  minutes=duetime[1])


    ## Skip posts specified in command line
    post_type = str(post.get('type'))
    if skip:
        if post_type in skip:
            continue


    ## Print reflections thread info
    if (duedate):
        print('--> Post cid=%d Title:%s Due:%s' % (post_cid, subject, due))
    else:
        print('--> Post cid=%d Title:%s' % (post_cid, subject))

    people = this_post.get('change_log')
    post_names.append(subject)

    piazzaids = []
    for response in people:
        uid = response.get('uid')
        if uid in profs:
            # Skip all non-student responses
            continue

        if (duedate):
            # Get date for each response, round down by nearest minute
            when = response.get('when').split('T')
            d = list(map(int, when[0].split('-')))
            t = when[1].split(':')
            rdate = datetime.datetime(d[0], d[1], d[2], int(t[0]), int(t[1]))
            if (rdate > due):
                print('    Response by %s (%s) too late, not counted' %
                        (sdict.get(uid), uid))
                print('      (response date: %s)' % rdate)
                continue

        # Put data in IDs list
        if uid not in profs:
            piazzaids.append(response.get('uid'))
    nresponse = len(piazzaids)
    print('     %d Responses.' % nresponse)

    if (DEBUG):
        for keys,var in this_post.items():
            print(str(keys),'=>',str(var))

    # Grade based on completion
    for s in students:
        partip_score = 0
        s_id = str(s[2])
        if s_id in piazzaids:
            partip_score = 1

        # append to students array
        s.append(partip_score)

    # Count number of posts
    nposts = nposts + 1
    tviews = tviews + views

print('Found %d total posts with %d total votes' % (nposts, tviews))
print('')

# Average all poll columns
for s in students:
    poll_grades = s[3::]
    total_grade = sum(poll_grades)
    s.append(total_grade)

# Output file
f = open(fname,'w')

# Write header
f.write('name,email,piazza_id,')
for i in range(nposts):
    f.write('%s,' % post_names[i])
f.write('total\n')

# write students list to file
for s in students:
    for i in range(nposts+3):
        f.write('%s,' % s[i])
    f.write('%d\n' % s[-1])
print('Data written to: %s' % fname)
f.close()

sys.exit()
