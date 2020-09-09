##This is Magic Link Authorization System.

For start you need create and activate virtual environment, then clone this repo.  

After that run:  
`pip install -r requirements.txt`  
`flask db init`  
`flask db migrate`  
`flask db upgrade`  
`flask run`

Server start on <a>localhost:5000</a> so go on this address in your browser.  

###How it works.  

#####I built this project based on Flask.
I installed and used the following extensions:  
>Flask Mail (for sending letters)  
>Flask SQLAlchemy (for interaction with the database)  
>Flask Migrate (for database interaction)  

I also used the built-in python libraries:  
>secrets (for generate token)  
>hashlib (for generate hash)  


When the main page is opened, the user sees the field and the send button. To register and receive a magic link, the user must enter an email and click button.  
Then app generates a token and hashcode based on the user's email, saves the user's email, hashcode and token in the database, then generates a magic link consisting of an email hash and a token separated by '_and_'.  

After that, a letter with this magical link is formed and sent to the user's mail. The user is redirected to the page with a request to check his e-mail.  
When the user clicks on the link in the letter, app check if the hash and token match the existing data in the database. If successful, it increases by one value in the login counter and user is redirected to the profile page. On this page user can see the count of logins and can to log out of the account.  

The user session is based on the `flask.session` object. When the user clicks on the magic link, app sets the new `key:value` pair (`user:user_email`) in the `session` object, which is deleted if the user clicks the logout button. 

There is also a decorator that gives access to the profile page only for authorized users.  

Also I create a test Gmail account to send emails via this app.
