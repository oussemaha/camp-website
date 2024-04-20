import os
from flask import Blueprint, render_template,url_for,redirect,request,session,jsonify,flash
from werkzeug.utils import secure_filename
import hashlib
from datetime import datetime

user = Blueprint('user',__name__)

@user.route("/")
def base():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")

@user.route("/dashboard")
def dash():
    if "user" in session:
        return render_template("dashboard.html",name=session["user"].title())
    return redirect("/login")

@user.route("/adherent")
def adherent():
    if "user" in session:
        return render_template("adherent.html",name=session["user"].title(),perms=session["perms"])
    return redirect("/login")

@user.route("/updateAdh")
def updateAdh():
    from main import mysql
    n=[]
    cur=mysql.connect.cursor()
    cur.execute("select count(*) from adherent where idcamp = %s",(session["idcamp"],))
    n.append(cur.fetchall()[0][0])
    cur.execute("select count(*) from adherent where idcamp = %s and idChambre is not null",(session["idcamp"],))
    n.append(cur.fetchall()[0][0])
    for i in ["Robotique","Informatique","Astronomie","Petit deb"]:
        cur.execute("select count(*) from adherent where idcamp = %s and idChambre is not null and section = %s ",(session["idcamp"],i))
        n.append(cur.fetchall()[0][0])
    cur.execute("select idadherent , prenom , nom , section , idChambre from adherent where idcamp = %s",(session["idcamp"],))
    l=cur.fetchall()
    cur.close()
    return jsonify(tableAdhHtml=render_template("updateAdh.html",adhL=l,perms=session["perms"]),totN=n)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@user.route("/ajouterAdh",methods=['GET','POST'])
def ajouterAdh():
    if 1 in session["perms"]:
        if request.method=="POST":
            from main import mysql,app
            con=mysql.connection    
            file = request.files['avatar']
            cur=con.cursor()
            cur.execute("insert into adherent (prenom,nom,tel,telParent,remarque,email,section,idcamp,date_de_naissance) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (request.form["prenom"],request.form["nom"],int(request.form["teladh"]),int(request.form["telParent"]),request.form["remarque"],
               request.form["emailadh"],request.form["section"],session["idcamp"],request.form["date de naissance"]))
            con.commit()
                
            if file.filename!='' and allowed_file(file.filename):
                cur.execute("select idadherent from adherent where prenom = %s and nom=%s and date_de_naissance = %s",
                    (request.form["prenom"],request.form["nom"],request.form["date de naissance"]))
                idAd=cur.fetchall()[0][0]
                filename= secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], str(idAd)+"."+filename.rsplit('.', 1)[1].lower()))
                cur.execute("update adherent set pdpType = %s where idadherent= %s ",(filename.rsplit('.', 1)[1].lower(),idAd))
                con.commit()
                cur.close()
                return redirect("/adherent")
            cur.close()
            return redirect("/ajouterAdh")
        else:
            return render_template("ajouteradh.html",name=session["user"].title())
    else : 
        return redirect("/adherent")

@user.route("/modifierAdh/<idAd>",methods=["GET","POST"])
def modifierAdh(idAd):

    if 3 in session["perms"]:
        from main import mysql,app
        con=mysql.connection
        cur=con.cursor()
        if request.method=="POST":
            file = request.files['avatar']
            cur.execute("update adherent set prenom=%s,nom=%s,tel=%s,telParent=%s,remarque=%s,email=%s,section=%s,date_de_naissance=%s  where idadherent= %s",
                (request.form["prenom"],request.form["nom"],int(request.form["teladh"]),int(request.form["telParent"]),request.form["remarque"],
               request.form["emailadh"],request.form["section"],request.form["date de naissance"],idAd))
            con.commit()
            if file.filename!='' and allowed_file(file.filename):
                cur.execute("select idadherent from adherent where prenom = %s and nom=%s and date_de_naissance = %s",
                    (request.form["prenom"],request.form["nom"],request.form["date de naissance"]))
                idAd=cur.fetchall()[0][0]
                filename= secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], str(idAd)+"."+filename.rsplit('.', 1)[1].lower()))
                cur.execute("update adherent set pdpType = %s where idadherent= %s ",(filename.rsplit('.', 1)[1].lower(),idAd))
                con.commit()
            return redirect("/adherent")    
        else :
            cur.execute("select prenom,nom,date_de_naissance,email,idChambre,tel,telParent,adresse,section,remarque from adherent where idadherent=%s ",(idAd,))
            l=cur.fetchall()
            return render_template("modifierAdh.html",name=session["user"].title(),content=l[0])
    else :
        return redirect("/")

@user.route("/profileAdh/<idAd>")
def profileAdh(idAd):
    from main import mysql,app
    con=mysql.connection
    cur=con.cursor()
    cur.execute("select prenom,nom,email,idChambre,tel,telParent,adresse,section,remarque,pdpType,date_de_naissance from adherent where idadherent=%s ",(idAd,))
    l=cur.fetchall()
    if len(l)>0:
        try:
            return render_template("adherentPerson.html",values=l[0],age=calculate_age(l[0][10]),pdp="pdp/"+str(idAd)+"."+l[0][9],perms=session["perms"],i=idAd)
        except:
            return render_template("adherentPerson.html",values=l[0],age=calculate_age(l[0][10]),pdp="NONE",perms=session["perms"],i=idAd)
    return redirect("/")

@user.route("/supprimerAdh/<idAd>")
def supprimerAdh(idAd):
    if 2 not in session["perms"]:
        return redirect("/")
    from main import mysql,app
    con=mysql.connection
    cur=con.cursor()
    cur.execute("delete from adherent where idadherent = %s",(idAd,))
    con.commit()
    con.close()
    return redirect("/adherent")

@user.route("/animateur")
def animateur():
    if "user" in session:
        return render_template("animateur.html",name=session["user"].title(),perms=session["perms"])
    return redirect("/login")

@user.route("/updateAnimateur")
def updateAnimateur():
    from main import mysql
    n=[]
    cur=mysql.connect.cursor()
    cur.execute("select count(*) from utilisateur u,user_group ug where ug.username=u.username and idcamp = %s and idGroup=1",(session["idcamp"],))
    n.append(cur.fetchall()[0][0])
    for i in ["Robotique","Informatique","Astronomie","Petit deb"]:
        cur.execute("select count(*) from utilisateur u,user_group ug where ug.username=u.username and idcamp = %s and idGroup=1 and section = %s ",(session["idcamp"],i))
        n.append(cur.fetchall()[0][0])
    cur.execute("select u.username, section , idchambre,numeroTel from utilisateur u,user_group ug where ug.username=u.username and idcamp = %s and idGroup=1  ",(session["idcamp"],))
    l=cur.fetchall()
    cur.close()
    return jsonify(tableAnimateurHtml=render_template("updateAnimateur.html",adhL=l,perms=session["perms"]),totN=n)

@user.route("/ajouterAnimateur",methods=['GET','POST'])
def ajouterAnimateur():
    if 4 in session["perms"]:
        if request.method=="POST":
            from main import mysql,app
            con=mysql.connection    
            file = request.files['avatar']
            cur=con.cursor()
            cur.execute("insert into utilisateur (username,passwd,numeroTel,email,cin,date_de_naissance,section,remarque,adresse,telUrgence) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (request.form["Username"],hashlib.sha512(request.form["passwd"].encode('UTF-8')).hexdigest(),int(request.form["telAnimateur"]),request.form["emailanimateur"],
                int(request.form["CIN"]),request.form["date de naissance"],request.form["section"],request.form["remarque"],request.form["adresse"],int(request.form["telUrgence"])))
            con.commit()
            cur.execute("insert into user_group values (%s,%s,%s)",(1,request.form["Username"],session["idcamp"]))    
            con.commit()
            if file.filename!='' and allowed_file(file.filename):
                filename= secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], request.form["Username"]+"."+filename.rsplit('.', 1)[1].lower()))
                cur.execute("update utilisateur set pdpType = %s where username= %s ",(filename.rsplit('.', 1)[1].lower(),request.form["Username"]))
                con.commit()
                cur.close()
                return redirect("/animateur")
            cur.close()
            return redirect("/ajouterAdh")
        else:
            return render_template("ajouterAnimateur.html",name=session["user"].title())
    else : 
        return redirect("/adherent")
@user.route("/profileAdh/<idAnimateur>")
def profileAnimateur(idAnimateur):
    from main import mysql,app
    con=mysql.connection
    cur=con.cursor()
    cur.execute("select numeroTel,email,cin,date_de_naissance,tel,telParent,adresse,section,remarque,pdpType,date_de_naissance from adherent where idadherent=%s ",(idAd,))
    l=cur.fetchall()
    if len(l)>0:
        try:
            return render_template("adherentPerson.html",values=l[0],age=calculate_age(l[0][10]),pdp="pdp/"+str(idAd)+"."+l[0][9],perms=session["perms"],i=idAd)
        except:
            return render_template("adherentPerson.html",values=l[0],age=calculate_age(l[0][10]),pdp="NONE",perms=session["perms"],i=idAd)
    return redirect("/")
@user.route("/login",methods=['GET','POST'])
def login():
    session.pop("user",None)
    session.pop("perms",None)
    session.pop("idCamp",None)
    if request.method=='POST':
        from main import mysql
        username=request.form["username"]
        password=request.form["password"]
        cur =mysql.connect.cursor()
        users=cur.execute("select * from utilisateur where username = %s and passwd = %s",(username,hashlib.sha512(password.encode('UTF-8')).hexdigest()))
        if users>0:
            session["user"]=username
            session["perms"]=[]
            return redirect("/chooseCamp")
    return render_template("login.html")
@user.route("/chooseCamp",methods=['GET','POST'])
def chooseCamp():
    from main import mysql
    con=mysql.connection
    if request.method=="POST":
        session["idcamp"]=request.form["Camp"]
        cur=con.cursor()
        cur.execute("select idpermission from user_group ug, group_permission gp where gp.idgroup=ug.idGroup and username=%s and idcamp=%s",(session["user"],session["idcamp"]))
        for i in cur.fetchall():
            session["perms"].append(i[0])
        return redirect('/')
    else:    
        cur=con.cursor()
        cur.execute("select  distinct * from (select periode , lieu , ug.idcamp  from user_group ug,camp c where ug.idcamp=c.idcamp and username=%s) a",(session["user"],))
        camps=cur.fetchall()
        return render_template("chooseCamp.html",campl=camps)

    
def calculate_age(birthdate):
    current_date = datetime.now()
    age = current_date.year - birthdate.year
    if current_date.month < birthdate.month or (current_date.month == birthdate.month and current_date.day < birthdate.day):
        age -= 1  
    return age
