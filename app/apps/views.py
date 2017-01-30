from . import apps
from random import randint
from flask import render_template, flash, url_for, session
from flask_wtf import Form
from wtforms import IntegerField, SubmitField
from wtforms.validators import Required, NumberRange

class GuessNumberForm(Form):
    number = IntegerField(u'Please guess a number between 0 and 1000:', 
                          validators=[Required(u'Please input a valid number'), 
                          NumberRange(0, 1000, u'the number should be 0 - 1000') ])
    submit = SubmitField(u'Submit')

@apps.route('/guess_number', methods=['GET', 'POST'])
def guess_number():
    #Generate an integer between 0 and 1000, and save it in session
    session['number'] = randint(0, 1000)
    session['times'] = 10

    times = session['times']
    result = session.get('number') 
    form = GuessNumberForm()
    if form.validate_on_submit():
        times -= 1
        session['times'] = times
        if times == 0:
            flash(u'Failed to guess the right number ....o(>_<)o')
            flash(u'The real number is {}'.format(result))
            return redirect(ur_for('main.index'))
        answer = form.number.data
        if answer > result:
            flash(u'Too big! you still have %s times chance' % times)
        elif answer < result:
            flash(u'Too small! you still have %s times chance' % times)
        else:
            flash(u'You win')
    return render_template('guess.html', form=form)

