from flask import Flask
app = Flask(__name__)


@app.route('/')
def index():
    return 'Tech Nights!!! home page'

@app.route('/schedule/')
@app.route('/schedule/upcoming')
def schedule_index():
    return 'schedule placeholder.  show upcoming schedules from now() onwards'


@app.route('/schedule/previous')
def schedule_previous():
    return 'schedule placeholder.  show upcoming schedules from now() onwards'


@app.route('/schedule/add')
def schedule_previous():
    return 'Add new schedule placeholder '


@app.route('/schedule/edit')
def schedule_previous():
    return 'Edit a schedule placeholder '



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5005)
