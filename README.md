
# Open access publishing service
## Python Flask
### Depending:
* python3
* flask
* flask-wtf
* flask-sqlalchemy
* flask-mail
* flask-login
* flask-uploads
* flask-script
* pillow

#### Persistent deployment on the server: ***106.53.21.189:8080***
#### Technology stack:
1.Tencent cloud Ubuntu server,uWSGI(main),nginx,supervisor(maybe don't work)
#### attention
order:1.register 2.log 3.activate 4.publish 5.comment

In order to prevent page loss caused by jumping to the page before loading successfully, add pageloader to see the page after loading, please wait patiently.
### [Project server address:](http://106.53.21.189:8080 "abc")

### Function Implemented:
* #### Beautiful static page(new)
1.***Pageloader,Sweat-heart,Rotated-background*** special effects.
* #### register(new)
1.Users should ***register*** before login.
* #### login(new)
1.After register,use the information to ***login***.
* #### Email(improve)
1. Users should ***validate*** their email address before publish and comment.
2. Server will send email to ***validate*** and ***notificate*** user about their action such as publishing and making comment.
3. **_Bad users will be banned_** by email.(remove)
* #### Publishing(improve)
1. Upload a pdf(new:or jpg,png) file to publish an article **_with a validated email_**
* #### Searching(improve)
1. Users can search articles by title, subject, author, email.
* #### Reading Article
1. People can see information and download the pdf(png,jpg) file.
* #### Comment
1. Make a comment **_with a validated email address_** under an article.
* #### Vote
1. Users can vote up or down to an article or a comment.
2. Each ip address can **_only vote once_** to an article or a comment.
* #### Other
1. Bad Ip address will be banned to access the website.(remove)
2.Use standard file directories instead of clutter one.(improve)
* #### Bug
1.I don't have time to debug 'read the article',so you can't read.
2.etc.