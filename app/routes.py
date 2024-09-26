from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
def index():
    user = {'username':'Peter'}
    posts = [
         {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Morioh-city!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Feidarras movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)