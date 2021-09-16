Backend:

The Server runs on Python3 with Flask
Server Dependencies:

* flask
* flask-cors
* requests

I've hidden CLIEND_ID and CLIENT_SECRET in a file named usertokens.json which I didn't upload to GitHub for security reasons.
usertokens should be put in Server/static directory. 

Then, run the server from the Server directory via "python3 app.py" command.

Frontend:

The frontend does not require a localserver. Just open the index.html with a browser and it works if the flask server is running.