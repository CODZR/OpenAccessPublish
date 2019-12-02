from flask_wtf.form import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired, FileField
from wtforms import PasswordField, SubmitField, TextAreaField, StringField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, ValidationError
from models import Article, User
import datetime
from captcha import getCaptcha


class LoginForm(FlaskForm):
    # openid=StringField('openid',validators=[DataRequired()])#Datarequired()确保字段中有数据
    remember_me = BooleanField('Remember me')
    nickname = StringField('Nickname', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign in')


class RegistrationForm(FlaskForm):
    nickname = StringField('Nickname', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password1', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')

    def validate_nickname(self, nickname):
        user = User.query.filter_by(nickname=nickname.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')



class UploadForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(min=1, max=50)])
    author = StringField("Author", validators=[DataRequired()])
    subject = StringField("Subjects", validators=[DataRequired()], render_kw={'placeholder': 'Split subjects by space'})
    highlight = TextAreaField("Highlight")
    email = StringField("Email", validators=[DataRequired(), Email(message="email error")],
                        render_kw={'placeholder': 'Email'})
    file = FileField("File(img)", validators=[FileRequired(), FileAllowed(['pdf','png','jpg'])])
    submit = SubmitField("Submit", render_kw={'class': 'btn btn-primary'})

    def to_Article(self):
        return Article(title=self.title.data, author=self.author.data, highlight=self.highlight.data,
                       subject=self.subject.data, date=datetime.datetime.now(), email=self.email.data)


class CommentForm(FlaskForm):
    email = StringField("Email(You should activate your email beform you comment)",
                        validators=[DataRequired(), Email(message="email error")],
                        render_kw={'placeholder': 'Email'})
    comment = TextAreaField("Comment",
                            validators=[DataRequired(), Length(min=5, message='At least 5 letters!')])
    submit = SubmitField("Submit", render_kw={'class': 'btn btn-primary'})


class SearchArticleForm(FlaskForm):
    content = StringField("Search:", render_kw={"class": "form-control"}, validators=[DataRequired()])
    submit = SubmitField("Submit", render_kw={'class': 'btn btn-primary'})


class EmailValidateForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(message="email error")],
                        render_kw={'placeholder': 'Email'})
    submit = SubmitField("Submit", render_kw={'class': 'btn btn-primary'})
