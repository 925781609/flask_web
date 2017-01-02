from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, BooleanField, ValidationError
from wtforms.validators import  Required, Length, Email, Regexp
from ..models import Role, User
from flask_pagedown.fields import PageDownField

class EditProfileForm(Form):
    name = StringField('Real name', validators=[Length(0,64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(Form):
    email = StringField('Email', validators=[Required(), Length(1,64), Email()])
    username = StringField('Username', validators=[Required(), Length(1,64), Regexp('^[a-zA-X][0-9a-zA-Z._]*$', 0, 
                            'Usernames must have only letters, numbers, dots or underscores')])
    confirmed = BooleanField('Confirm')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[ Length(0, 64)])
    location = StringField('Location', validators=[ Length(0, 64)])
    about_me = TextAreaField('About me')
    sbumit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already registered.')

class PostForm(Form):
    #body = TextAreaField("What's on your mind?", validators=[Required()])
    body = PageDownField("What's on your mind?", validators=[Required()])
    submit = SubmitField('Submit')


class CommentForm(Form):
    body = StringField('', validators=[Required()])
    submit = SubmitField('Submit')
