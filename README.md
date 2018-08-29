# piazza_tools
Tools for getting data from piazza (teaching/discussion platform) to make my life easier

HEAVILY relies on [piazza-api](https://github.com/hfaran/piazza-api) for all
connections and calls to piazza

#
### details
tools/
--> get_polls-api.py

usage: python2 get_polls-api.py class_id yes-grading

finds all polls in your piazza class, grades for either participation or based
on the "poll explanation" option used when creating the poll. Checks are made to
ensure that the poll has its results visible to instructors only (public and
private polls are ignored), published, and votes. Polls with up to 6 answers are
supported.



### other
No docs yet, maybe someday.
