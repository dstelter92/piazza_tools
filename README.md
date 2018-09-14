# piazza_tools
Tools for getting data from piazza (teaching/discussion platform) to make my life easier

HEAVILY relies on [piazza-api](https://github.com/hfaran/piazza-api) for all
connections and calls to piazza

#
### tools/
--> get_polls-api.py

usage: python2 get_polls-api.py -c classid -e login_email -g yes/no

finds all polls in your piazza class, grades for either participation or based
on the "poll explanation" option used when creating the poll. Checks are made to
ensure that the poll has its results visible to instructors only (public and
private polls are ignored), published, and votes. Polls with up to 6 answers are
supported. Grades are tabulated and written to a csv file.


--> querry_posts-api.py

usage: python2 querry_posts-api.py -c classid -e login_email -s skip_type -q search_querry  

gets all posts matching search_querry and checks which students have posted any
response to them. Participation grades are then tabulated and written to a csv
file.


--> post_reflections-api.py

usage: python2 querry_posts-api.py -c classid -e login_email -t title -n nsects
-s status

posts a 'reflections' thread for for nsects groups on piazza. Somewhat
specialized for my usage, but a good example on how to create an instructor post
and assign it to a group with pre-set content.


### other
No docs yet, maybe someday.
