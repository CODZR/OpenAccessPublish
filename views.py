from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

from app import app, db, lm, mail
from flask import render_template, flash, redirect, g, request, send_from_directory, abort, session, make_response, \
    url_for
from forms import *
from models import *
from flask_mail import Message
import datetime
import re
import os
from threading import Thread
from tools import remove_captcha, remove_article, remove_comment, showhide_article, check_text, remove_img


# from tools import remove_captcha,remove_img 放在view里是为了import顺序，若在app.py导入则报错，因为这两个方程还未from app import db

class Email(db.Model):
    email = db.Column(db.String(40), primary_key=True)
    validated = db.Column(db.String(10))
    validate_time = db.Column(db.DateTime)
    password = db.Column(db.String(100))
    ban = db.Column(db.String(10))

    def is_exist(self):
        num = Email.query.filter_by(email=self.email).count()
        if num > 0:
            e = Email.query.filter_by(email=self.email).first()
            self.validated = e.validated
            self.validate_time = e.validate_time
            self.password = e.password
            return True
        return False

    def is_banned(self):
        if self.ban == 'yes':
            return True
        return False

    def is_validated(self):
        if self.is_banned():
            return False
        if self.validated == 'yes':
            return True
        return False

    def __init__(self, email=None, is_validate='no', password='', validate_time=None, ban='no'):
        self.email = email
        self.validated = "no"
        self.validate_time = validate_time
        self.password = password
        self.ban = ban

    def generate_password(self):
        pwd = str(int(datetime.datetime.now().strftime("%Y%m%d%H%M%S")) % 1000000007)
        e = str(self.email)
        pwd += re.sub('[@.]', '', e)
        self.password = pwd
        return str(pwd)


def sendEmailBackground(msg):
    with app.app_context():
        mail.send(msg)


def sendEmail(msg):
    thr = Thread(target=sendEmailBackground, args=[msg])
    thr.start()


def getSubjectTree():
    '''
    Every Subject is save as a class with a list named 'children', which contains all it children(not grandchild).
    :return:
    a list of all subject on root
    '''
    subjects = []
    level1st = Subject.query.filter_by(depth=0).all()
    for s1 in level1st:
        s1.__init__()
        level2nd = Subject.query.filter_by(super_subject=s1.id).all()
        for s2 in level2nd:
            s2.__init__()
            level3rd = Subject.query.filter_by(super_subject=s2.id).all()
            for s3 in level3rd:
                s2.children.append(s3)
            s1.children.append(s2)
        subjects.append(s1)
    return subjects


@app.route('/index')
def index():
    arts = Article.query.filter_by(is_hide='no').all()
    for a in arts:
        a.getVisit()
        a.getPoint()
    arts = sorted(arts)
    # get the subject tree
    subjects = getSubjectTree()
    rsp = make_response(render_template('index.html', title="OPEN ACCESS PUBLISHING", articles=arts, subjects=subjects))
    rsp.set_cookie('online', '1')
    return rsp


@app.before_request
def before_request():
    if current_user.is_authenticated:
        # current_user.last_seen = datetime.utcnow()
        db.session.commit()


# 从数据库加载用户
@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    # print('begin login',current_user.is_authenticated)
    if current_user.is_authenticated:  # 如果当前的用户已经登陆
        print('is login')
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():  # form.nickname.data
        # db.create_all()
        user = User.query.filter_by(nickname=form.nickname.data).first()
        if user.check_user(form.password.data):
            user.is_authenticated = True
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')

        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('Login.html',
                           title='Home',
                           form=form)


# 注册视图
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(nickname=form.nickname.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', title="Register", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


# using session to limit repeat request
def check_session(limit=5):
    t1 = 0;
    if session.get('timestamp') is not None:
        t1 = session.get('timestamp')
    delta = time.time() - t1
    session['timestamp'] = time.time()
    if (delta > limit):
        return True
    return False


# publish an article
@app.route('/publish', methods=['POST', 'GET'])
def publish():
    '''
    If recieve a post, then regard as a publish form.
    A form will create an article class and do related work
    :return:
    '''
    if not check_session(3):
        abort(404)
    form = UploadForm()
    captcha = getCaptcha()
    msg = "You should only upload pdf,jpg,png files.And please be patient!"
    if request.method == 'POST':
        if form.validate_on_submit():
            e = Email(email=form.email.data)
            if e.is_exist() and e.is_validated():
                # Every module below are independent

                # generate an article and add it
                article = form.to_Article()
                for s in CSsubject:
                    if s == article.subject:
                        article.subject = 'Computer Sciences'
                article.id = str(1)
                a_num = int(Article.query.count())
                if a_num > 0:
                    article.id = str(int(Article.query.order_by(Article.id.desc()).first().id) + 1)
                temp = form.file.data.filename
                filepath = os.path.splitext(temp)
                file_name, type = filepath
                print(type)
                article.img = str(article.id) + type
                filename = os.path.join(app.root_path, "static", "img", article.id + type)
                form.file.data.save(filename)

                # if a subject is not exist, then create it
                sub = Subject.query.filter_by(name=article.subject).first()
                if sub is None:
                    sub = Subject()
                    sub.name = article.subject
                    sub.super_subject = 0
                    sub.depth = 0
                    db.session.add(sub)
                db.session.commit()
                db.session.add(article)

                # generate a record and add it
                record = IpRecord()
                record.ip = request.remote_addr
                record.page = "publish"
                record.target_id = int(article.id)
                db.session.add(record)

                # after all work done, commit it
                db.session.commit()

                # send email
                email_msg = Message(recipients=[form.email.data], subject='[OPEN ACCESS PUBLISH]Publish notification')
                email_msg.body = 'CLICK HERE TO VALIDATE'
                email_msg.html = "<h1>Notification</h1><p>You have published an <a href='http://106.53.21.189:5000/detail/%s'>article</a></p>" % (
                    str(
                        article.id))
                sendEmail(email_msg)

                return redirect('/detail/' + str(article.id))
            else:
                msg = "You must activate your email address before you publish"

    return render_template('publish.html', form=form, title='Publish', message=msg, captcha=captcha)


@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchArticleForm()
    if request.method == 'POST':
        content = form.content.data
        a = Article(title=content, author=content, subject=content, email=content)
        articles = Article.query.filter(Article.title.like("%%%s%%" % a.title) |
                                        Article.author.like("%%%s%%" % a.author) |
                                        Article.subject.like("%%%s%%" % a.subject)).filter_by(is_hide='no').order_by(
            Article.id.desc()).all()
        comments = Comment.query.filter(Comment.content.like("%%%s%%" % content)).all()
        return render_template('search.html', list=articles, form=form, commentlist=comments)
    articles = Article.query.filter_by(is_hide='no').order_by(Article.id.desc()).all()
    return render_template('search.html', list=articles, form=form)


@app.route('/detail/<int:article_id>', methods=['GET', 'POST'])
def detail(article_id):
    captcha = getCaptcha()
    form = CommentForm()
    article = Article.query.filter_by(id=article_id, is_hide='no').first()
    if article is not None:
        record = IpRecord()
        record.page = "detail"
        record.ip = request.remote_addr
        record.target_id = article_id
        db.session.add(record)
        db.session.commit()
        # vis = int(IpRecord.query.filter_by(target_id=article_id, page="detail").group_by("ip").count())
        # article.visit = vis
        comments = Comment.query.filter_by(target=article.id).order_by(Comment.date.desc()).all()
        msg = 'Please input more than 5 words or you can\'t make comments.'
        if request.method == 'POST':  # post a comment
            if form.validate_on_submit() and check_session():
                e = Email(email=form.email.data)
                if e.is_exist() and e.is_validated():
                    # generate a comment and add it
                    comment = Comment(target=article.id, content=check_text(form.comment.data), email=form.email.data,
                                      id=1)
                    t_num = int(Comment.query.count())
                    if t_num > 0:
                        comment.id = Comment.query.order_by(Comment.id.desc()).first().id + 1
                    comment.date = datetime.datetime.now()
                    db.session.add(comment)

                    db.session.commit()

                    # email actions
                    email_msg = Message(recipients=[e.email], subject="Notification")
                    email_msg.html = """<h1>Notication</h1><p>Your email has made a comment 
                    on <a href='http://106.53.21.189:5000/detail/%s'>website</a></p>""" % str(article_id)
                    sendEmail(email_msg)
                    print('test11111')
                    return redirect('/detail/' + str(article_id))
        return render_template('detail.html', form=form, title='Detail', message=msg, article=article,
                               comments=comments,
                               captcha=captcha)
    abort(404)


@app.route('/download/<article_img>', methods=['GET'])
def download_img(article_img):
    if not check_session():
        abort(404)
    return send_from_directory('static/img', article_img)


@app.route('/vote/<target_type>/<vote_type>/<vote_id>', methods=["POST"])
def vote(target_type, vote_type, vote_id):
    if request.method == "POST":
        if vote_type == "up" or vote_type == "down":
            if target_type == "comment":
                if int(Comment.query.filter_by(id=vote_id).count()) > 0:
                    if VoteComment.query.filter_by(target_id=vote_id, ip=request.remote_addr,
                                                   type=vote_type).count() > 0:
                        VoteComment.query.filter_by(target_id=vote_id, ip=request.remote_addr, type=vote_type).delete()
                    else:
                        v = VoteComment(target_id=vote_id, ip=request.remote_addr, date=datetime.datetime.now(), id=1,
                                        type=vote_type)
                        if int(VoteComment.query.count()) > 0:
                            v.id = VoteComment.query.order_by(VoteComment.id.desc()).first().id + 1
                        db.session.add(v)
                    db.session.commit()
                    cnt = VoteComment.query.filter_by(target_id=vote_id, type=vote_type).count()
                    Comment.query.filter_by(id=vote_id).update({'vote' + vote_type: cnt})
                    db.session.commit()
                    return str(cnt)
            elif target_type == "article":
                if Article.query.filter_by(id=vote_id).count() > 0:
                    if VoteArticle.query.filter_by(target_id=vote_id, ip=request.remote_addr,
                                                   type=vote_type).count() > 0:
                        VoteArticle.query.filter_by(target_id=vote_id, ip=request.remote_addr, type=vote_type).delete()
                    else:
                        v = VoteArticle(target_id=vote_id, ip=request.remote_addr, date=datetime.datetime.now(), id=1,
                                        type=vote_type)
                        if VoteArticle.query.count() > 0:
                            v.id = VoteArticle.query.order_by(VoteArticle.id.desc()).first().id + 1
                        db.session.add(v)
                    db.session.commit()
                    cnt = VoteArticle.query.filter_by(target_id=vote_id, type=vote_type).count()
                    Article.query.filter_by(id=vote_id).update({'vote' + vote_type: cnt})
                    db.session.commit()
                    return str(cnt)
    abort(404)


@app.route('/ckvote/<target_type>/<vote_type>/<vote_id>', methods=["POST"])
def ckvote(target_type, vote_type, vote_id):
    if request.method == "POST":
        if vote_type == "up" or vote_type == "down":
            if target_type == "comment":
                if int(Comment.query.filter_by(id=vote_id).count()) > 0:
                    if VoteComment.query.filter_by(target_id=vote_id, ip=request.remote_addr,
                                                   type=vote_type).count() > 0:
                        return "1"
                    else:
                        return '0'
            elif target_type == "article":
                if Article.query.filter_by(id=vote_id).count() > 0:
                    if VoteArticle.query.filter_by(target_id=vote_id, ip=request.remote_addr,
                                                   type=vote_type).count() > 0:
                        return "1"
                    else:
                        return "0"
    abort(404)


@app.route('/validator/<statu>', methods=['GET', 'POST'])
@app.route('/validator/<statu>/<recieve_email>', methods=['GET', 'POST'])
def email_validate(statu, recieve_email=None):
    if recieve_email is None:
        if statu == 'activate':
            form = EmailValidateForm()
            if request.method == 'POST':
                if form.validate_on_submit():
                    return redirect('/validator/validation/%s' % form.email.data)
            return render_template('validate.html', title='Validate the email', form=form)
    else:
        e = Email()
        e.email = recieve_email
        if statu == 'validation':
            if not e.is_exist():
                e.generate_password()
                email_msg = Message(recipients=[recieve_email], subject='OPEN ACCESS PUBLISH validation ',
                                    sender="975336710@qq.com")
                email_msg.body = 'CLICK HERE TO VALIDATE'
                email_msg.html = "<h1>Activation</h1><p><a href='http://106.53.21.189:5000/captcha/%s'>Click to activate</a></p>" % e.password
                sendEmail(email_msg)
                e.validate_time = datetime.datetime.now()
                db.session.add(e)
                db.session.commit()
                return "We've already send you an validation email.<a href='/validator/activate'>Back</a>"
            elif not e.is_validated():
                return "<a href='/validator/resend/%s'>Didn't receive email?</a>" % recieve_email
            else:
                print(123)
                return "<a href='/validator/activate'>You hava validated!</a>"
        elif statu == 'resend':
            if e.is_exist():
                if not e.is_validated():
                    email_msg = Message(recipients=[recieve_email], subject='OPEN ACCESS PUBLISH validation ',
                                        sender="975336710@qq.com")
                    email_msg.body = 'CLICK HERE TO VALIDATE'
                    email_msg.html = "<h1>Activation</h1><p><a href='http://localhost:5000/captcha/%s'>Click to activate</a></p>" % e.password
                    sendEmail(email_msg)
                    return "We've already send you an validation email.<a href='/validator/activate'>Back</a> "
            abort(404)
    abort(404)


@app.route('/captcha/<password>', methods=['GET'])
def validate_captcha(password):
    num = Email.query.filter_by(password=password, validated='no').count()
    if num > 0:
        Email.query.filter_by(password=password).update({'validated': 'yes'})
        db.session.commit()
        return "Activation Success!<a href='/index'>Back</a>"
    abort(404)


@app.route('/donate')
def donation():
    return render_template('donate.html', title="Donation")


@app.route('/captcha', methods=['GET', 'POST'])
def checkCaptcha():
    if request.method == 'POST':
        return getCaptcha()
    abort(400)


# @app.before_request
# def ip_filter():
#     online=request.cookies.get('online')
#     if online!=1:
#         return redirect('/')
#     ip = request.remote_addr
#     if BadUser.query.filter_by(ip=ip).count() > 0:
#         abort(403)
#     return


@app.route('/author')
def authorpage():
    email = request.args.get('email')
    email = base64.b64decode(email)
    a = Article.query.filter_by(email=email).all()
    c = Comment.query.filter_by(email=email).all()
    return render_template('author.html', title='Author Page', article=a, comment=c, email=email)


@app.route('/subject')
def subject_list():
    sub = request.args.get('subject')
    if sub is not None:
        articles = Article.query.filter_by(subject=sub).all()
        for a in articles:
            print(a)
            a.getVisit()
            a.getPoint()
        articles = sorted(articles)
        return render_template('subjectlist.html', title="Subject:" + sub, articles=articles)
    return redirect('/index')


@app.route('/admin/<action>')
@app.route('/admin')
def administrator(action=None):
    if action is None:
        return render_template("admin.html", title="Admin", table=None)
    elif action == 'captcha':
        remove_captcha()
        return "yes"
    elif action == 'img':
        remove_img()
        return "yes"
    elif action == 'articles':
        a = ArticleTable()
        return render_template("admin.html", title="Admin", table=a)

    elif action == 'comments':
        c = CommentTable()
        return render_template("admin.html", title="Admin", table=c)
    elif action == 'badword':
        b = BadWordTable()
        return render_template('admin.html', title="admin bad words", table=b)
    abort(404)


# future work:add permission check
@app.route('/admin/<action>/<int:id>/<type>')
def admin_remove(action, id, type):
    if action == 'delete':
        if type == 'article':
            if remove_article(id):
                return "yes"
        elif type == 'comment':
            if remove_comment(id):
                return "yes"
    elif action == 'hide' or action == 'show':
        showhide_article(id, action)
        return "yes"
    abort(404)

    @app.route('/admin/subject/add', methods=['GET', 'POST'])
    def add_subject():
        form = SubjectForm()
        if request.method == 'POST' and form.validate_on_submit():
            s = Subject()
            s.name = form.name.data
            ts = Subject.query.filter_by(name=form.father.data).first()
            s.super_subject = 0
            if ts is not None:
                s.super_subject = int(ts.id)
            s.depth = form.depth.data
            db.session.add(s)
            db.session.commit()
            return redirect('/admin/subject/add')
        return render_template("admin.html", title="add subject", form=form)
