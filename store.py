import os
import github
from counter import Counter
from operator import itemgetter
from dictionaries import DotDict, PersistentDict
import omnijson as json
import config

def load_data(organisation_name, update=False):
    data = {}
    path = '%s/%s.json' % (config.STORE, organisation_name)
    if os.path.exists(path) and not update:
        with open(path, 'rb') as f:
            data = json.loads(f.read())
    else:
        organisation = github.organisation(organisation_name)
        projects = [repository['name'] for repository in github.organisation_repositories(organisation_name)]
        pull_request_map = {}
        pull_request_comments_map = {}
        pull_requests = []
        pull_request_comments = []
        projects_with_pulls = []

        for project in projects:
            pulls, comments = github.pull_requests_with_comments(organisation_name, project, state='closed')
            print '[load_data] %s: got %d pull requests with %d comments' % (project, len(pulls), len(comments))
            open_pulls, open_comments = github.pull_requests_with_comments(organisation_name, project, state='open')
            print '[load_data] %s: got %d open pull requests with %d comments' % (project, len(open_pulls), len(open_comments))
            pulls += open_pulls
            comments += open_comments

            pull_request_map[project] = pulls
            pull_request_comments_map[project] = comments

            pull_requests += pulls
            pull_request_comments += comments

            if pulls:
                projects_with_pulls.append(project)

        data = {
            'pull_requests'                    : pull_requests,
            'pull_requests_per_project'        : pull_request_map,

            'pull_request_comments'            : pull_request_comments,
            'pull_request_comments_per_project': pull_request_comments_map,

            'projects'                         : projects,
            'projects_with_pulls'              : projects_with_pulls,
            'organisation'                     : organisation,
        }
        with PersistentDict(path, 'c', format='json') as d:
            d.update(data)

    return data

def open_pull_requests(organisation):
    data = load_data(organisation)
    return [pull for pull in data['pull_requests'] if pull['state']=='open']

def count_per_user(items, count_key=None):
    items = [{'login':key, 'count':value} for key, value in Counter([x.get('user', {}).get('login') for x in items if x['user']]).items()]
    aggregate = sorted(items, key=itemgetter('count'), reverse=True)
    return aggregate

def aggregate_data(organisation):
    data = load_data(organisation)

    total_pull_counts = count_per_user(data['pull_requests'])
    total_comment_counts = count_per_user(data['pull_request_comments'])

    project_counts, user_counts = aggregate_stats(organisation)

    data = {
        'raw'         : data,
        'user_avatars': map_user_avatars(organisation),
        'projects'    : project_counts,
        'users'       : user_counts,
        'totals': {
            'pulls'   : total_pull_counts,
            'comments': total_comment_counts,
        },
        'organisation': data['organisation'],
    }
    return data

def map_user_avatars(organisation):
    data = load_data(organisation)
    user_avatar_map = {}
    for item in data['pull_requests'] + data['pull_request_comments']:
        user_avatar_map[(item['user'] or {}).get('login')] = (item['user'] or {})['avatar_url'] if item['user'] else None

    return user_avatar_map

def aggregate_stats(organisation):
    data = load_data(organisation)

    project_counts = DotDict({})
    user_counts = DotDict({})

    for project in data['projects_with_pulls']:
        # retrieve pulls for a project
        project_pulls = data['pull_requests_per_project'][project]
        comments = data['pull_request_comments_per_project'][project]

        # calculate the pull request leaderboard for this project
        project_counts['%s.pulls' % project] = count_per_user(project_pulls)
        project_counts['%s.comments' % project] = count_per_user(comments)

        # create user/project and project/user keyed transformations
        for user in project_counts[project]['pulls']:
            # user_counts['michael']['supporttools']['pulls'] = 5
            user_counts['%s.%s.pulls' % (user['login'], project)] = user['count']
            # projects_counts['supporttools']['michael']['pulls'] = 5
            project_counts['%s.%s.pulls' % (project, user['login'])] = user['count']

        for user in project_counts[project]['comments']:
            # user_counts['michael']['supporttools']['comments'] = 5
            user_counts['%s.%s.comments' % (user['login'], project)] = user['count']
            # project_counts['supporttools']['michael']['comments'] = 5
            project_counts['%s.%s.comments' % (project, user['login'])] = user['count']

    return project_counts, user_counts

