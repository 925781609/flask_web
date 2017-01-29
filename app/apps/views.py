from . import apps
from random import randint
from flask import render_template, flash, url_for
from flask_wtf import Form
from wtforms import Integer

class GuessNumberForm(Form):
    number = IntegerField(u'Please guess a number between 0 and 1000:', 
                          validators=[Required(u'Please input a valid number'), 
                          NumberRange(0, 1000, u'the number should be 0 - 1000') ])
    submit = SubmitField(u'Submit')

@apps.route('/guess_number', methods=['GET'])
def guess_number():
    #Generate an integer between 0 and 1000, and save it in session
    session['number'] = randint(0, 1000)
    session['times'] = 10

    times = session['times']
    result = session.get('number') 
    form = GuessNumberForm()
    if form.valid_on_submit():


    return "Pls guess a number"

