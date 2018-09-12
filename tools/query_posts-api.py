#!/usr/bin/python2

import sys, argparse
import getpass
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
parser.add_argument('-q', '--query', metavar='quary', type=str, nargs='*',
        help='Search query')
parser.add_argument('-s', '--skip', metavar='skip', type=str, nargs='*',
        help='Skip post type (question / poll / note)')

args = parser.parse_args()
classid = args.classid
email = args.email
query = ' '.join(args.query)
skip = args.skip

fname = 'query-%s_participation-%s.csv' % (query,classid)

print 'Connecting to Piazza via piazza-api...'

# Piazza setup
p = Piazza()
p.user_login(email=email,password=None)
me = p.get_user_profile()
pclass = p.network(classid)
print '  Logged in as:', me.get('name')
print ''

# Get user list of name, email and piazza_id
print 'Finding all students in Piazza class:',classid
users = pclass.get_all_users()
students = []
profs = []
for user in users:
    # Get data from piazza API
    student_name = str(user.get('name'))
    student_email = str(user.get('email'))
    piazza_ID = str(user.get('id'))

    # Check to make sure they are a student
    role = user.get('role')
    if role != 'student':
        ## Debug check to print Prof/TA info
        print '--> IGNORE Prof/TA:',student_name,piazza_ID
        profs.append(piazza_ID)
        continue

    # Put data into list
    data = [student_name,student_email,piazza_ID]
    students.append(data)
print 'Found',len(students),'students'
print ''


# Get poll posts
posts = pclass.search_feed(query)
print 'Searching posts containing "',query,'" for completed polls to grade based on correctness...'
post_names = []
nposts = 0
tviews = 0
for post in posts:
    post_cid = int(post.get('nr'))
    subject = str(post.get('subject'))
    views = int(post.get('unique_views'))
    this_post = pclass.get_post(post_cid)


    ## Skip posts specified in command line
    post_type = str(post.get('type'))
    if skip:
        if post_type in skip:
            continue


    print '--> Poll cid=',post_cid,' title:',subject
    people = this_post.get('change_log')
    post_names.append(subject)

    piazzaids = []
    for response in people:
        uid = response.get('uid')
        if uid not in profs:
            piazzaids.append(response.get('uid'))
    nresponse = len(piazzaids)
    print '    ',nresponse,'responses.'

    if (DEBUG):
        for keys,var in this_post.items():
            print(str(keys),'=>',str(var))

    # Skip if no answers... something went wrong.
    if (nresponse == 0):
        print 'WARNING: Poll cid=',post_cid,'has no responses, skipping...'
        continue

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

print 'Found',nposts,'total polls with',tviews,'total votes'
print ''

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
print 'Data written to:',fname
f.close()

sys.exit()
