#!/usr/bin/env python3
import datetime
import json
import os
import urllib.parse

import requests


class Milestoner:
    def __init__(self, *, owner, repo):
        self.github_api_token = os.environ['MILESTONER_GITHUB_API_TOKEN']
        self.owner = owner
        self.repo = repo
        self.existing_milestones_data = None

    def github_request(self, verb, subject, data=None, query=None):
        headers = {
            'Authorization': f'token {self.github_api_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        prefix = 'https://api.github.com/repos'
        query_string = '?' + urllib.parse.urlencode(query) if query else ''
        url = f'{prefix}/{self.owner}/{self.repo}/{subject}{query_string}'
        response = getattr(requests, verb)(
            url, data=json.dumps(data) if data else None, headers=headers
        )
        if response.status_code >= 400:
            print(f'Request failed for {verb} {url} !')
            print(response.json())
        return response.json()

    def get_desired_milestones(self, num=5):
        """Return the list of desired milestone dates.

        Note: we end up recomputing this for every repos, which is annoying
        but doesn't really matter for the scope of this script - it's not going
        to be a bottleneck anyway."""
        desired_milestones = []
        year, week, day = datetime.date.today().isocalendar()
        for target in range(week, min(53, week + num)):  # 53 for leap years.
            try:
                thursday = datetime.date.fromisocalendar(year, target, 4)
            except ValueError:
                print('Skipping week {target}, it is missing the target day')
            desired_milestones.append(thursday)
        return desired_milestones

    def fetch_existing_open_milestones(self):
        """Fetch existing opened milestones. This call is cached on the
        instance.

        We assume we'll never get more than one page of 30 items - we should be
        closing them regularly.
        """
        if self.existing_milestones_data is None:
            self.existing_milestones_data = self.github_request('get', 'milestones')
        existing_milestones = []
        for data in self.existing_milestones_data:
            try:
                milestone = datetime.datetime.strptime(data['title'], '%Y.%m.%d').date()
                existing_milestones.append(milestone)
            except ValueError:
                print(f'Ignoring broken existing milestone {data["title"]}')
        print(f'We currently have {existing_milestones} on {self.repo}')
        return existing_milestones

    def create_next_milestones(self):
        """Check milestones on the target repo and creates the next x missing
        weekly milestones if necessary."""
        # Build names of milestones we would normally create.
        desired_milestones = self.get_desired_milestones()
        print(f'We want to have {desired_milestones}')

        # Gather existing milestones.
        existing_milestones = self.fetch_existing_open_milestones()

        # Find the ones we're missing.
        missing_milestones = set(desired_milestones).difference(existing_milestones)
        print(f'We are missing {missing_milestones} on {self.repo}')

        # Create them, including due date 48 hours before target.
        for milestone in missing_milestones:
            # Due date needs to be 2 days before the target milestone date, and
            # it needs to be a datetime object with timezone so get ISO 8601
            # format.
            due_date = milestone - datetime.timedelta(days=2)
            due_date = datetime.datetime.combine(
                due_date, datetime.datetime.min.time()
            ).replace(tzinfo=datetime.timezone.utc)
            data = {
                'title': milestone.strftime('%Y.%m.%d'),
                'state': 'open',
                'description': '',
                'due_on': due_date.isoformat(),
            }
            data = self.github_request('post', 'milestones', data=data)
            if 'id' in data:
                print(f'Created milestone {milestone} on {self.repo}')
            else:
                print(f'Failed to create milestone {milestone} on {self.repo}')
                print(data)

    def close_previous_milestones(self):
        """Close milestones that have a due date more than 3 days in the
        past."""
        # Load the raw milestone_data we'll need if we don't already have it,
        # but ignore the return value, it's not enough for what we need here.
        if self.existing_milestones_data is None:
            self.fetch_existing_open_milestones()
        now = datetime.datetime.now()
        for milestone_data in self.existing_milestones_data:
            due_date = datetime.datetime.fromisoformat(
                milestone_data['due_on'].strip('Z')
            )
            if now > due_date + datetime.timedelta(days=3):
                print(f'Closing milestone {milestone_data["title"]} on {self.repo}')
                data = {'state': 'closed'}
                self.github_request(
                    'patch', f'milestones/{milestone_data["number"]}', data=data
                )


if __name__ == '__main__':
    repos = (
        'addons',
        'addons-frontend',
        'addons-server',
        'addons-linter',
        'addons-code-manager',
        'addons-blog',
    )
    for repo in repos:
        m = Milestoner(owner='mozilla', repo=repo)
        m.create_next_milestones()
        m.close_previous_milestones()
