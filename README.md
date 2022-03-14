# Backend Coding Challenge

[![Build Status](https://github.com/Thermondo/backend-code-challenge/actions/workflows/main.yml/badge.svg?event=push)](https://github.com/Thermondo/backend-code-challenge/actions)

We appreciate you taking the time to participate and submit a coding challenge. In the next step we would like you to
create/extend a backend REST API for a simple note-taking app. Below you will find a list of tasks and limitations
required for completing the challenge.

### Application:

* Users can add, delete and modify their notes
* Users can see a list of all their notes
* Users can filter their notes via tags
* Users must be logged in, in order to view/add/delete/etc. their notes

### The notes are plain text and should contain:

* Title
* Body
* Tags

### Optional Features 🚀

* [ ] Search contents of notes with keywords
* [ ] Notes can be either public or private
    * Public notes can be viewed without authentication, however they cannot be modified
* [ ] User management API to create new users

### Limitations:

* use Python / Django
* test accordingly

### What if I don't finish?

Try to produce something that is at least minimally functional. Part of the exercise is to see what you prioritize first when you have a limited amount of time. For any unfinished tasks, please do add `TODO` comments to your code with a short explanation. You will be given an opportunity later to go into more detail and explain how you would go about finishing those tasks.


## Setting up Virtualenv

1. `pip install virtualenv`
2. `virtualenv venv`
3. `source venv/bin/activate` (to get out of the virtual environment, just enter `deactivate` into your terminal)
4. `pip install -Ur requirements.txt`

## Running the database migrations

5. `python app/manage.py migrate`

## Running the test server

6. `python app/manage.py runserver`

## Running the unit tests

7. `python app/manage.py test api`

If everything went well, you should have a message like this:

Ran 14 tests in 0.588s
OK

Otherwise, the report will follow:

FAILED (failures=1)

## Getting the coverage report

1. `pip install coverage`

2. `coverage run app/manage.py test api`

3. `coverage report`
