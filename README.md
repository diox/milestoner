# Purpose

Automatically creates and closes weekly milestones on `mozilla/addons`, `mozilla/addons-frontend`, `mozilla/addons-server`, `mozilla/addons-linter`, `mozilla/addons-code-manager` and `mozilla/addons-blog`.

## Installing

It requires Python 3.8+ with `requests`.

Once installed, you need to set the `MILESTONER_GITHUB_API_TOKEN` environnement variable with a valid github API token that can retrieve and modify milestones for the repositories.

## Running

Run `./milestoner.py`. It accepts no arguments at the moment. It will automatically create missing milestones for the next 5 weeks and close old ones with a due date more than 3 days in the past.
