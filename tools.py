import os
import re

from app import app

# Delete all rubbish data in database after a time
from app import db
from models import BadWord, Article, VoteArticle, Comment, VoteComment


def delete_rubbish():
    pass


def check_text(str):
    s = str
    res = BadWord.query.all()
    for r in res:
        s = re.sub(r.word, '  ', s)
    return s


def remove_captcha():
    for file in os.listdir(os.path.join(app.root_path, 'static', 'captcha')):
        os.unlink(os.path.join(app.root_path, "static", "captcha", file))


def remove_img():
    for file in os.listdir(os.path.join(app.root_path, 'static', 'img')):
        os.unlink(os.path.join(app.root_path, "static", "img", file))


def remove_article(id):
    a = Article.query.filter_by(id=id).first()
    if a is not None:
        os.unlink(os.path.join(app.root_path, 'static', 'img', a.pdf))  # remove files
        vote = VoteArticle.query.filter_by(target_id=a.id).all()
        for v in vote:  # remove related votes
            db.session.delete(v)
        comments = Comment.query.filter_by(target=a.id).all()
        for c in comments:  # remove related comments
            db.session.delete(c)
        db.session.delete(a)
        db.session.commit()
        return True
    return False


def showhide_article(id, action):
    if action == 'hide':
        Article.query.filter_by(id=id).update({'is_hide': 'yes'})
    else:
        Article.query.filter_by(id=id).update({'is_hide': 'no'})
    db.session.commit()


def remove_comment(id):
    c = Comment.query.filter_by(id=id).first()
    if c is not None:
        vote = VoteComment.query.filter_by(target_id=c.id).all()
        for v in vote:
            db.session.delete(v)
        db.session.delete(c)
        db.session.commit()
        return True
    return False


'''
Physical Sciences
    Physics
        Astronomy
	Quantum Mechanics
    Chemistry
    Environmental Sciences
Social Sciences
    Anthropology
    Sustainability Science
Biological Sciences
    Cell Biology
    Genetics
    Neuroscience **
    Plant Biology
    Developmental Biology
    System Biology
    Biochemistry
    Biophysics and Computational Biology
Computer Sciences
    Machine Learning
    Computational Biology
    Computational Complexity
    Computational Linguistics
Statistics
    Applied Statistics
    Mathematical Statistics
Mathematics
    Graphy Theory
    Number Theory
Medical Sciences
    Breast Cancer
    Ebola Virus
    Epidemics
    Dermatology General
    Immunity
    Obesity
    Neuroscience **
    
    INSERT INTO subject (id, depth, name, super_subject) VALUES (1, 0, 'Physical Sciences', '0');
INSERT INTO subject (id, depth, name, super_subject) VALUES (2, 1, 'Physics', '1');
INSERT INTO subject (id, depth, name, super_subject) VALUES (3, 2, 'Astronomy', '2');
INSERT INTO subject (id, depth, name, super_subject) VALUES (4, 1, 'Quantum Mechanics', '1');
INSERT INTO subject (id, depth, name, super_subject) VALUES (5, 1, 'Chemistry', '1');
INSERT INTO subject (id, depth, name, super_subject) VALUES (6, 1, 'Environmental Sciences', '1');
INSERT INTO subject (id, depth, name, super_subject) VALUES (7, 0, 'Social Sciences', '0');
INSERT INTO subject (id, depth, name, super_subject) VALUES (8, 1, 'Anthropology', '7');
INSERT INTO subject (id, depth, name, super_subject) VALUES (9, 1, 'Sustainability Science', '7');
INSERT INTO subject (id, depth, name, super_subject) VALUES (10, 0, 'Biological Sciences', '0');
INSERT INTO subject (id, depth, name, super_subject) VALUES (12, 1, 'Plant Biology', '10');
INSERT INTO subject (id, depth, name, super_subject) VALUES (13, 1, 'Developmental Biology', '10');
INSERT INTO subject (id, depth, name, super_subject) VALUES (14, 1, 'System Biology', '10');
INSERT INTO subject (id, depth, name, super_subject) VALUES (15, 1, 'Biochemistry', '10');
INSERT INTO subject (id, depth, name, super_subject) VALUES (16, 1, 'Biophysics and Computational Biology', '10');
INSERT INTO subject (id, depth, name, super_subject) VALUES (17, 0, 'Computer Sciences', '0');
INSERT INTO subject (id, depth, name, super_subject) VALUES (18, 1, 'Machine Larning', '17');
INSERT INTO subject (id, depth, name, super_subject) VALUES (19, 1, 'Computational Biology', '17');
INSERT INTO subject (id, depth, name, super_subject) VALUES (20, 1, 'Computational Complexity', '17');
INSERT INTO subject (id, depth, name, super_subject) VALUES (21, 1, 'Computational Linguistics', '17');
INSERT INTO subject (id, depth, name, super_subject) VALUES (22, 0, 'Statistics', '0');
INSERT INTO subject (id, depth, name, super_subject) VALUES (23, 1, 'Applied Statistics', '22');
INSERT INTO subject (id, depth, name, super_subject) VALUES (24, 1, 'Mathematical Statistics', '22');
INSERT INTO subject (id, depth, name, super_subject) VALUES (25, 0, 'Mathematics', '0');
INSERT INTO subject (id, depth, name, super_subject) VALUES (26, 1, 'Graphy Theory', '25');
INSERT INTO subject (id, depth, name, super_subject) VALUES (27, 1, 'Number Theory', '25');
INSERT INTO subject (id, depth, name, super_subject) VALUES (28, 0, 'Medical Sciences', '0');
INSERT INTO subject (id, depth, name, super_subject) VALUES (29, 1, 'Breast Cancer', '28');
INSERT INTO subject (id, depth, name, super_subject) VALUES (30, 1, 'Ebola Virus', '28');
INSERT INTO subject (id, depth, name, super_subject) VALUES (31, 1, 'Epidemics', '28');
INSERT INTO subject (id, depth, name, super_subject) VALUES (32, 1, 'Dermatology General', '28');
INSERT INTO subject (id, depth, name, super_subject) VALUES (33, 1, 'Immunity', '28');
INSERT INTO subject (id, depth, name, super_subject) VALUES (34, 1, 'Obesity', '28');
INSERT INTO subject (id, depth, name, super_subject) VALUES (35, 1, 'Neuroscience', '28');
'''
