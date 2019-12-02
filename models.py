from _md5 import md5

from flask_login import UserMixin
from flask_login._compat import unicode
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from app import app, db, lm
import datetime
import re
import time
import base64

# for users (unavailable)
ROLE_USER = 0
ROLE_ADMIN = 1

CSsubject = ['CS', 'computer science', 'Computer Science', 'ComputerScience', 'CompSci']


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=False, nullable=False)
    password = db.Column(db.String(120), index=True, unique=False, nullable=False)
    # about_me = db.Column(db.String(140))
    # last_seen = db.Column(db.DateTime, default=datetime.utcnow().isoformat())
    is_authenticated = False
    is_active = True
    is_anonymous = False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    # def avatar(self, size):
    #     # return 'http://www.gravatar.com/avatar/' + md5(self.email.encode('utf-8')).hexdigest() + '?d=mm&s=' + str(size)
    #     digest = md5(self.email.lower().encode('utf-8')).hexdigest()
    #     return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
    #         digest, size)

    def check_user(self, password):  # 检查密码是否正确
        if self.password == password:
            return True
        else:
            return False

    def __repr__(self):
        return '<User %r>' % self.nickname


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    depth = db.Column(db.Integer, default=0)
    name = db.Column(db.String(50), unique=True)
    super_subject = db.Column(db.String(30))

    def __init__(self):
        self.children = []


class Article(db.Model):
    def __str__(self):
        return "ID:%s title:%s" % (self.id, self.title)

    def __lt__(self, other):
        return self.point > other.point

    def getEmail(self):
        return re.sub("\\S{1,3}@\\S+", '**@**', self.email)

    def getB64Email(self):
        return base64.b64encode((self.email).encode())

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50))
    author = db.Column(db.String(50))
    highlight = db.Column(db.Text)
    subject = db.Column(db.String(50), db.ForeignKey('subject.name'))
    email = db.Column(db.String(50))
    date = db.Column(db.DateTime)
    img = db.Column(db.String(100))
    voteup = db.Column(db.Integer, default=0)
    votedown = db.Column(db.Integer, default=0)
    is_hide = db.Column(db.String(10), default='no')
    point = 0
    visit = 0

    def getVisit(self):
        self.visit = int(IpRecord.query.filter_by(target_id=self.id, page="detail").group_by("ip").count())
        return self.visit

    def getPoint(self):
        now = time.time()
        t1 = self.date.timestamp()
        delta_time = now - t1
        vote = self.voteup * 1.0 / (self.votedown + 1.0)
        self.point = (self.visit / delta_time * 100) * 0.3 + vote * 0.7
        return self.point


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    target = db.Column(db.Integer, db.ForeignKey("article.id"))
    content = db.Column(db.Text)
    date = db.Column(db.DateTime)
    voteup = db.Column(db.Integer, default=0)
    votedown = db.Column(db.Integer, default=0)

    def getEmail(self):
        return re.sub("\\S{1,3}@\\S+", '**@***', self.email)


class Vote():
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(50))
    date = db.Column(db.DateTime)
    type = db.Column(db.String(50), default="up")


class VoteArticle(Vote, db.Model):
    target_id = db.Column(db.Integer, db.ForeignKey("article.id"))
    pass


class VoteComment(Vote, db.Model):
    target_id = db.Column(db.Integer, db.ForeignKey("comment.id"))
    pass


class BadUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    ip = db.Column(db.String(20))


class BadWord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(50))


class IpRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ip = db.Column(db.String(50))
    page = db.Column(db.String(50))
    target_id = db.Column(db.Integer)


class Table:
    def __init__(self):
        self.name = ''
        self.thead = []
        self.items = []


class CommentTable(Table):
    def __init__(self):
        super().__init__()
        self.name = 'comment'
        self.thead.append('ID')
        self.thead.append("email")
        self.thead.append('target')
        self.thead.append('content')
        self.thead.append("date")
        self.thead.append('voteup')
        self.thead.append('votedown')
        comments = Comment.query.all()
        for c in comments:
            row = []
            row.append(c.id)
            row.append(c.email)
            row.append(c.target)
            row.append(c.content)
            row.append(c.date)
            row.append(c.voteup)
            row.append(c.votedown)
            self.items.append(row)


class ArticleTable(Table):
    def __init__(self):
        super().__init__()
        self.name = 'article'
        self.thead.append('ID')
        self.thead.append('Title')
        self.thead.append('Author')
        self.thead.append('Highlight')
        self.thead.append('Subject')
        self.thead.append('Email')
        self.thead.append('Date')
        self.thead.append('Pdf')
        self.thead.append('voteup')
        self.thead.append('votedown')
        articles = Article.query.all()
        for a in articles:
            row = []
            row.append(a.id)
            row.append(a.title)
            row.append(a.author)
            row.append(a.highlight)
            row.append(a.subject)
            row.append(a.email)
            row.append(a.date)
            row.append(a.pdf)
            row.append(a.voteup)
            row.append(a.votedown)
            self.items.append(row)


class BadWordTable(Table):
    def __init__(self):
        super().__init__()
        self.name = 'bad word'
        self.thead.append('id')
        self.thead.append('word')
        bad_words = BadWord.query.all()
        for b in bad_words:
            row = []
            row.append(b.id)
            row.append(b.word)
            self.items.append(row)


class SubjectForm(FlaskForm):
    formname = "subject"
    name = StringField("Name", validators=[DataRequired()])
    father = StringField("Father", validators=[DataRequired()])
    depth = StringField("Depth", validators=[DataRequired()])
    submit = SubmitField("Submit")
