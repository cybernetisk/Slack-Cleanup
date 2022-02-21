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
   1) `SLACK_TOKEN=<token> poetry run cleanup`

## How to configure


## How to test functions
### The message

* Config the test target 
* Run `SLACK_TOKEN=<token> poetry run test-msg`

