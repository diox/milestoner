# Purpose

Automically creates weekly milestones for the next 5 weeks on `mozilla/addons`, `mozilla/addons-frontend`, `mozilla/addons-server`, `mozilla/addons-linter` and `mozilla/addons-code-manager`.

## Installing

Because it requires Python 3.8 as well as requests, it can be a little annoying to install. You can use pyenv + a virtualenv, or a docker image with python 3.8 and requests installed.

Once installed, you need to set the `MILESTONER_GITHUB_API_TOKEN` environnement variable with a valid github API token that can retrieve and modify milestones for the repositories.

## Running

Run `./milestoner.py`. It accepts no arguments at the moment. It will automatically create missing milestones (and close old ones once this feature is implemented)
