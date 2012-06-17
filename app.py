from flask import Flask, render_template
from store import aggregate_data, open_pull_requests
from flaskext.markdown import Markdown
import config

app = Flask(__name__)
Markdown(app)
app.config.from_object('config')

@app.route('/')
def index():
    """Shows a leaderboard of users, in two categories: pull request creators
    and commenters"""
    data = aggregate_data(config.ORGANISATION_NAME)
    return render_template('index.html',
            avatars      = data['user_avatars'],
            pulls        = data['totals']['pulls'],
            comments     = data['totals']['comments'],
            projects     = data['raw']['projects'],
            organisation = data['organisation'])

@app.route('/user/<username>')
def user(username):
    """Show project stats for this user"""
    data = aggregate_data(config.ORGANISATION_NAME)
    return render_template('user.html',
            avatar        = data['user_avatars'][username],
            organisation  = data['organisation'],
            username      = username,
            user          = data['raw']['user_data'][username],
            project_stats = data['users'][username])

@app.route('/projects/<projectname>')
def project(projectname):
    """Show user stats for this project"""
    data = aggregate_data(config.ORGANISATION_NAME)

    project_stats = data['projects'][projectname]
    if project_stats:
        project_stats.pop('pulls')
        project_stats.pop('comments')

    return render_template('project.html',
            organisation  = data['organisation'],
            projectname   = projectname,
            project_stats = project_stats,
            project       = data['raw']['project_data'].get(projectname))

@app.route('/open-pull-requests')
def open_pulls():
    """Displays currently open pull requests"""
    pulls = open_pull_requests(config.ORGANISATION_NAME)
    data = aggregate_data(config.ORGANISATION_NAME)
    return render_template('open_pull_requests.html',
            open_pulls = pulls,
            avatars = data['user_avatars'])

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
