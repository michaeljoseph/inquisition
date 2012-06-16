from testify import TestCase, assert_equals, suite, class_setup
from store import count_per_user, load_data, map_user_avatars, aggregate_data, aggregate_stats
from github import pull_requests, pull_requests_with_comments, organisation_repositories, organisation

class GitHubTestCase(TestCase):

    @suite('pulls', 'integration')
    def test_pull_requests(self):
        pulls = pull_requests('yola', 'supporttools')
        assert isinstance(pulls, list)
        assert len(pulls) > 0
        assert_equals(len(pulls[0].keys()), 18)

    @suite('comments', 'integration')
    def test_pull_request_comments(self):
        pulls, comments = pull_requests_with_comments('yola', 'supporttools')
        assert isinstance(pulls, list)
        assert len(pulls) > 0
        assert_equals(len(pulls[0].keys()), 18)

        assert isinstance(comments, list)
        assert len(comments) > 0
        assert_equals(len(comments[0].keys()), 12)

    @suite('repos', 'integration')
    def test_organisation_repos(self):
        repos = organisation_repositories('yola')
        assert isinstance(repos, list)
        assert_equals(len(repos[0].keys()), 27)

    @suite('org', 'integration')
    def test_organisation(self):
        org = organisation('yola')
        assert isinstance(org, dict)
        assert_equals(len(org.keys()), 23)


class AggregationTestCase(TestCase):

    @suite('count')
    def test_count_per_user(self):
        raw_data = [
            {'user': {'login': u'dochead'}, 'title': u'Vader6046 git'},
            {'user': {'login': u'dochead'}, 'title': u'Vader6046 git'},
            {'user': {'login': u'musamhlengi'}, 'title': u"lockerz bundle dict missing 'name' key value pair"}
        ]

        expected = [{'count': 2, 'login': u'dochead'}, {'count': 1, 'login': u'musamhlengi'}]
        assert_equals(count_per_user(raw_data, 'username'), expected)


class PersistenceTestCase(TestCase):
    @class_setup
    def seed_data(self):
        self.organisation = 'yola'
        load_data(self.organisation)

    @suite('persist')
    def test_load_data(self):
        data = load_data(self.organisation)
        assert_equals(sorted(data.keys()), sorted(['pull_requests',
            'pull_requests_per_project',
            'pull_request_comments',
            'pull_request_comments_per_project',
            'projects',
            'projects_with_pulls']))

    @suite('avatar')
    def test_user_avatar_map(self):
        avatars = map_user_avatars(self.organisation)
        assert 'michaeljoseph' in avatars.keys()
        assert avatars['michaeljoseph'].startswith('https://secure.gravatar.com/avatar')

    @suite('aggregate')
    def test_aggregate_data(self):
        data = aggregate_data(self.organisation)
        assert_equals(sorted(data.keys()), sorted(['raw', 'user_avatars', 'projects', 'users', 'totals']))

    @suite('aggregate-stats')
    def test_pull_and_comment_stats(self):
        project_counts, user_counts = aggregate_stats(self.organisation)

        for thing_type in ['pulls', 'comments']:
            for project in project_counts.keys():
                item = project_counts[project][thing_type]
                if item:
                    user = item[0]['login']
                    pull_count = item[0]['count']
                    assert_equals(user_counts[user][project][thing_type], pull_count)

    @suite('update')
    def test_update_data(self):
        data = load_data('github')
        assert data

#class FrontEndTestCase(TestCase):
    #def setUp(self):
        #self.app = application.test_client()

    #@suite('ui-index')
    #def test_index(self):
        #rv = self.app.get('/')
        #assert 'Chief Yank Requestors' in rv.data


