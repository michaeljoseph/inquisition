import requests
import omnijson as json
import config

def extract(d, keys):
    extracted = dict((k, d[k]) for k in keys if not isinstance(k, list) and k in d)
    for key in keys:
        if isinstance(key, list):
            value = d[key.pop(0)]
            for k in key:
                value = value[k]
            extracted[key[0]] = value
    return extracted

def github_api(path, data=None):
    return requests.get('https://api.github.com' + path, data=data, auth=(config.GITHUB_USER, config.GITHUB_PASSWORD))

def pull_requests(user, repository, state='closed'):
    pulls = []

    response = github_api('/repos/%(user)s/%(repository)s/pulls' % {'user': user, 'repository': repository}, data={'state':state})

    if response.ok:
        pulls = json.loads(response.content)
    return pulls

def pull_requests_with_comments(user, repository, state='closed'):
    pulls = []
    comments = []

    pulls = pull_requests(user, repository, state=state)

    if pulls:
        for pull_request in pulls:
            response = github_api('/repos/%(user)s/%(repository)s/pulls/%(pull_request_number)s/comments' % dict(user=user, repository=repository, pull_request_number=pull_request['number']))
            if response.ok:
                comments += json.loads(response.content)

    return pulls, comments

def organisation_repositories(organisation):
    repositories = []

    response = github_api('/orgs/%(organisation)s/repos' % {'organisation': organisation})

    if response.ok:
        repositories = [repository for repository in json.loads(response.content) if not repository['fork']]

    return repositories

def organisation(org):
    organisation = None
    response = github_api('/orgs/%(organisation)s' % {'organisation': org})
    if response.ok:
        organisation = json.loads(response.content)
    else:
        print response
    return organisation
