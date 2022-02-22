# Slack cleaner



## How to run

### Get the workspace information

1) Go here and download a export
   1) https://cybernetisk.slack.com/services/export
2) Unzip the folder into the workspace folder
   1) Workspace/<list of channels++>
3) Get the token from one of these links. Populate the auth.yaml.example file:
   1) https://wiki.cyb.no/display/X/Vaskehjelpe+creds
   2) https://api.slack.com/apps/A033TEQEQ30


### Run the program

1) Install python3.8
   1) `sudo apt install python3`
2) Install poetry in python3
   1) `sudo pip install poetry`
3) Install python env
   1) `poetry install`
4) Run script
   1) `poetry run cleanup`

## How to configure


## How to test functions
I opted for using PyTest to start off with.
In pycharm they are trivial to run, just navigate into the files in the tests folder and right-click


# What to do

## We need to define what is an inactive member
* Fetch channel message history
  * https://api.slack.com/methods/search.messages
    * For user in users:
      * Search from:@user in#channel
* Find all messages:
  * https://api.slack.com/methods/conversations.history
    * Find all messages back to timeout
      * Iterate over all
* Fetch channel events
  * Is it possible?
* Fetch user activity