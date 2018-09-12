#!/usr/bin/python2

import sys, argparse
import getpass
from piazza_api import Piazza

DEBUG = 0

## Command line args
parser = argparse.ArgumentParser(description='Get polls from piazza class'
    ', grade according to correct answer specified (explanation) in poll'
    ' or via participation.')
parser.add_argument('-c', '--classid', metavar='classID', type=str, nargs='?',
        help='Piazza classID from URL')
parser.add_argument('-g', '--grading', metavar='grading', type=str, nargs='?',
        help='Should grading be performed? (yes/no)', default='no')
parser.add_argument('-e', '--email', metavar='email', type=str, nargs='?',
        help='Piazza email to login with')

args = parser.parse_args()
grading = args.grading
classid = args.classid
email = args.email

## Grade poll based on answer or just check for completion? (yes=1, no=0)
if (grading == ''):
    GRADE_POLL = 0 # DEFAULT
elif (grading == 'no'):
    GRADE_POLL = 0
elif (grading == 'yes'):
    GRADE_POLL = 1
else:
    print 'Invalid grading option'
    sys.exit()

if (GRADE_POLL):
    fname = 'polls_graded-%s.csv' % classid
else:
    fname = 'polls_participation-%s.csv' % classid

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
        continue

    # Put data into list
    data = [student_name,student_email,piazza_ID]
    students.append(data)
print 'Found',len(students),'students'
print ''


# Get poll posts
posts = pclass.iter_all_posts()
if (GRADE_POLL):
    print 'Searching posts for completed polls to grade based on correctness...'
else:
    print 'Searching posts for completed polls to grade based on participation...'
poll_names = []
npoll = 0
nvotes = 0
for post in posts:
    post_cid = int(post.get('nr'))
    poll_data = post.get('data')

    # Skip posts that arn't polls
    post_type = str(post.get('type'))
    post_title = str(post.get('history')[0].get('subject'))
    if post_type != 'poll':
        continue

    # Skip polls that arn't anonymous to students
    # public and hidden from instructors shouldn't be graded
    poll_anon = str(post.get('config').get('anonymous'))
    if (poll_anon != 'stud'):
        continue

    # Also skip those that are unpublished
    unpublished = int(post.get('config').get('unpublished'))
    if (unpublished):
        continue

    if (DEBUG):
        for keys,var in post.items():
            print(str(keys),'=>',str(var))

    print '--> Poll cid=',post_cid,' title:',post_title

    # Skip if no answers... something went wrong.
    votes = int(poll_data.get('total_votes'))
    if (votes == 0):
        print 'WARNING: Poll cid=',post_cid,'has no votes, skipping...'
        continue

    poll_names.append(post_title)

    if (GRADE_POLL):
        # Check answer, match to poll integer
        answer = str(poll_data.get('answer'))
        if (answer == 'A' or answer == '1'):
            answer = 0
        elif (answer == 'B' or answer == '2'):
            answer = 1
        elif (answer == 'C' or answer == '3'):
            answer = 2
        elif (answer == 'D' or answer == '4'):
            answer = 3
        elif (answer == 'E' or answer == '5'):
            answer = 4
        elif (answer == 'F' or answer == '6'):
            answer = 5
        else:
            print 'WARNING: Poll cid=',post_cid,' has answer in an unsupported form.'
            print '  Use alphanumeric or integer answers for grading,'
            print '  6 answers MAX!! skipping...'
            continue

        # Grade poll, get ID for correct answers, then put in 'students' array
        results = poll_data.get('result').get(str(answer))
        for s in students:
            score = 0 ## score on this poll
            s_id = str(s[2])
            if s_id in results:
                score = 1

            # Append 'score' to students array
            s.append(score)
    else:
        # UNGRADED polls, just check for completion
        results = poll_data.get('result').values()
        all_results = [str(item) for sublist in results for item in sublist]
        for s in students:
            partip_score = 0 ## bool if they did this quiz
            s_id = str(s[2])
            if s_id in all_results:
                partip_score = 1

            # Append 'partip_score' to students array
            s.append(partip_score)

    # Count number of polls
    npoll = npoll + 1
    nvotes = nvotes + votes

print 'Found',npoll,'total polls with',nvotes,'total votes'
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
for i in range(npoll):
    f.write('%s,' % poll_names[i])
f.write('total\n')

# write students list to file
for s in students:
    for i in range(npoll+3):
        f.write('%s,' % s[i])
    f.write('%d\n' % s[-1])
print 'Data written to:',fname
f.close()

sys.exit()
