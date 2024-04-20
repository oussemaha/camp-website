from flask import Flask,session,url_for
from User import user
from flask_mysqldb import MySQL

UPLOAD_FOLDER = "./static/pdp"


app = Flask(__name__)
app.config["MYSQL_HOST"]="localhost"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_PASSWORD"]="*******"
app.config["MYSQL_DB"]="ajstcamp"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key="hola"
mysql= MySQL(app)

app.register_blueprint(user, url_prefix="/")

if __name__=="__main__":
    app.run(debug=True)