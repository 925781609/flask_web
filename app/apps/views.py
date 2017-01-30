from . import apps
from random import randint
from flask import render_template, redirect, flash, url_for, session
from flask_wtf import Form
from wtforms import IntegerField, SubmitField
from wtforms.validators import Required, NumberRange
start_to_guess  = 1
class GuessNumberForm(Form):
    number = IntegerField(u'Please guess a number between 0 and 1000:', 
                          validators=[Required(u'Please input a valid number'), 
                          NumberRange(0, 1000, u'the number should be 0 - 1000') ])
    submit = SubmitField(u'Submit')

@apps.route('/guess_number', methods=['GET', 'POST'])
def guess_number():
    #Generate an integer between 0 and 1000, and save it in session
    global start_to_guess
    if start_to_guess:
        session['number'] = randint(0, 1000)
        session['times'] = 10
        start_to_guess = 0
    print('guess_number() was called')
    times = session['times']
    result = session.get('number') 
    form = GuessNumberForm()
    if form.validate_on_submit():
        print('times is %s' % times)
        times -= 1
        session['times'] = times
        print("session['times'] is %s" % times)
        if times == 0:
            flash(u'Failed to guess the right number ....o(>_<)o')
            flash(u'The real number is {}'.format(result))
            start_to_guess = 1
            return redirect(url_for('main.index'))
        answer = form.number.data
        if answer > result:
            flash(u'Too big! you still have %s times chance' % times)
        elif answer < result:
            flash(u'Too small! you still have %s times chance' % times)
        else:
            flash(u'You win')
            start_to_guess = 1
            return redirect(url_for('main.index'))
    return render_template('guess.html', form=form)

