# primera prueba
from flask import Flask, render_template, url_for, request, redirect, jsonify, config, make_response
from flask import Response
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, Column , ForeignKey
from sqlalchemy import DateTime, Integer, String, Text, Float
from flask import g
import os
import re
import logging,sys
import datetime
from datetime import timedelta
import json
import sqlite3
from flask_wtf import FlaskForm
from wtforms import SelectField,StringField,validators
from sqlite3 import Error
from webargs import flaskparser, fields
from errors import InternalServerError

# flask Configuration
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
Bootstrap(app)
app.config['SECRET_KEY'] = 'secret'
db = SQLAlchemy(app)



# validations

def validation_message (Tabla,Filtro):     
    Numregistros = 0
    Numregistros = Tabla.query.filter_by(**Filtro).count()        
    if Numregistros == 0:
        message =  "No matches found in the table "+ Tabla.__tablename__
    else:
        message = ""    
        
    return message

def validation_messageWihoutFilter (Tabla):     
    Numregistros = 0
    Numregistros = Tabla.query.count()        
    if Numregistros == 0:
        message =  "No matches found in the table "+ Tabla.__tablename__
    else:
        message = ""    
        
    return message



    
# classes 


class Form_validations(FlaskForm):
    # StringField('Username', [validators.Length(min=4, max=25)])
    ThreatName =  StringField('ThreatName', [validators.Length(min=2, max=25)])
    ThreatDesc = StringField('ThreatDesc', [validators.Length(min=1, max=25)])

class Task_DB(db.Model):
    __tablename__ = "Task"
    IDTask                   = db.Column(db.Integer, primary_key= True)
    IDPlan                   = db.Column(db.Integer)
    IDIntel                  = db.Column(db.Integer)
    Orden                    = db.Column(db.String(100))

class Plan_DB(db.Model):
    __tablename__ = "Plan"
    IDPlan                   = db.Column(db.Integer, primary_key= True)
    IDThreat                 = db.Column(db.String(100))
    Name                     = db.Column(db.String(100))
    Description              = db.Column(db.String(500))

class DataStore_DB(db.Model):
    __tablename__ = "DataStore"
    # __bind_key__ = "DataStore"
    IDData                   = db.Column(db.Integer, primary_key= True)
    IDWarrior                = db.Column(db.Integer)
    User                     = db.Column(db.String(100))
    IP                       = db.Column(db.String(100))
    Password                 = db.Column(db.String(100))
    NTLM                     = db.Column(db.String(100))
    LM                       = db.Column(db.String(100))

class Threat_DB(db.Model):
    __tablename__ = "Threat"
    IDThreat                 = db.Column(db.Integer, primary_key= True)
    Created                  = db.Column(db.String(100))
    Modified                 = db.Column(db.String(100))
    Name                     = db.Column(db.String(100))
    Description              = db.Column(db.String(500))
    Windows                  = db.Column(db.String(100))
    MacOS                    = db.Column(db.String(100))
    Linux                    = db.Column(db.String(100))

class Inteligence_DB(db.Model):
    __tablename__ = "Inteligence"
    IDIntel                  = db.Column(db.Integer, primary_key= True)
    IDTech                   = db.Column(db.String(100))
    IDTactic                 = db.Column(db.String(100))
    Function                 = db.Column(db.String(500))
    Terminated               = db.Column(db.String(100))

class Technique_DB(db.Model):
    __tablename__ = "Technique"
    IDTech                   = db.Column(db.Integer, primary_key= True)
    URL_Mitre                = db.Column(db.String(500))
    Name                     = db.Column(db.String(100))
    IDMitre                  = db.Column(db.String(100), unique=True, nullable=False)

class Tactic_DB(db.Model):
    __tablename__ = "Tactic"
    IDTactic                 = db.Column(db.Integer, primary_key= True)
    URL_Mitre                = db.Column(db.String(100))
    Name                     = db.Column(db.String(100))
    Description              = db.Column(db.String(500))
    IDMitre                  = db.Column(db.String(100), unique=True, nullable=False)

class Warrior_DB(db.Model):
    __tablename__ = "Warrior"
    IDWarrior                   = db.Column(db.Integer, primary_key= True)
    State                       = db.Column(db.String(100))
    Legacy                      = db.Column(db.String(100))
    Alias                       = db.Column(db.String(100))
    Os                          = db.Column(db.String(100))
    Arch                        = db.Column(db.String(100))
    Name                        = db.Column(db.String(100))
    PID                         = db.Column(db.String(100))
    Lastseen                    = db.Column(db.String(100))
    IP                          = db.Column(db.String(100))

class Directive_DB(db.Model):
    __tablename__ = "Directive"
    IDDirective                     = db.Column(db.Integer, primary_key = True)
    IDWarrior                       = db.Column(db.Integer)
    IDTask                          = db.Column(db.Integer)
    Result                          = db.Column(db.String(2000))
    Done                            = db.Column(db.String(100))
    Good                            = db.Column(db.String(100))
    Privilege                       = db.Column(db.String(100))
class Form(FlaskForm):        
    tactic                   = SelectField('tactic', choices=[])
    intel                    = SelectField('intel', choices=[])
    threat                   = SelectField('threat', choices=[])
    plan                     = SelectField('plan', choices=[])

class Form_task(FlaskForm):        
    warrior                   = SelectField('warrior', choices=[])

class Warrior:
  def __init__(self,idw,os,arch,name,pid,timestamp,ip):
    self.IDWarrior           = idw
    self.os                  = os
    self.arch                = arch
    self.name                = name
    self.pid                 = pid
    self.lastseen            = timestamp
    self.ip                  = ip

class Threat:
  def __init__(self,id,name,description):
    self.id                  = id
    self.name                = name
    self.description         = description

class technique:
  def __init__(self,IDTech,URL_Mitre,Name,IDMitre):
    self.IDTech              = IDTech
    self.URL_Mitre           = URL_Mitre
    self.Name                = Name
    self.IDMitre             = IDMitre

class Tactic:
  def __init__(self,IDtactic,URL_Mitre,Name,Description,IDMitre):
    self.IDtactic            = IDtactic
    self.URL_Mitre           = URL_Mitre
    self.Name                = Name
    self.Description         = Description
    self.IDMitre             = IDMitre

class Result:
    def __init__(self,idw,idp,data):
        self.id              = idw
        self.plan            = idp
        self.resultado       = data

# funciones asociadas con la base de datos 

# Threat's inserts
def insertar_Amenaza(amenaza):
    # for amenaza in amenazas:           
    Numregistros = 0
    Numregistros = Threat_DB.query.filter_by(Name = amenaza['Name'] ).count()        
    if Numregistros == 0:
        registro = Threat_DB(
                # IDThreat =amenaza['IDThreat'],
                Created=amenaza['Created'],
                Modified=amenaza['Modified'],
                Name=amenaza['Name'],
                Description=amenaza['Description'],
                Windows=amenaza['Windows'],
                MacOS=amenaza['MacOS'],
                Linux=amenaza['Linux']
                )
        db.session.add(registro)    
        db.session.commit()  
        logging.debug('Amenaza insertada...')
        return (registro.IDThreat)     
    else:
       Threat = Threat_DB.query.filter_by(Name = amenaza['Name'] ).first()
       return (Threat.IDThreat)

# plan's inserts
def insertar_Plan(plan,Threat):    

    Numregistros = 0
    Numregistros = Plan_DB.query.filter_by(Name = plan['Name'] ).count()        
    if Numregistros == 0:
        registro = Plan_DB( 
                # IDPlan =plan['IDPlan'],
                IDThreat=Threat,
                Name=plan['Name'],
                Description=plan['Description']                    
                )
        db.session.add(registro)    
        db.session.commit() 
        logging.debug('plan insertado...')
        return (registro.IDPlan)
    else: 
        IDPlan = AvailablePlanName (plan, Threat)  
        return (IDPlan)
             
def AvailablePlanName(plan, Threat):

    Numregistros = 0
    loop = 0
    planName = plan['Name']
    notFound = False
    while notFound == False:  
        loop = loop + 1    
        planName =  plan['Name'] + "_"+str(loop)  
        Numregistros = Plan_DB.query.filter_by(Name = planName ).count()        
        if Numregistros == 0:
            notFound = True
    registro = Plan_DB( 
                # IDPlan =plan['IDPlan'],
                IDThreat=Threat,
                Name=planName,
                Description=plan['Description']                    
                )
    db.session.add(registro)    
    db.session.commit()   
    
    return (registro.IDPlan)    


# tech's inserts
def insertar_Tecnica(tecnica):   
    Insert_Tecnicas = []
    Numregistros = 0
    Numregistros = Technique_DB.query.filter_by(IDMitre = tecnica['IDMitre'] ).count()        
    if Numregistros == 0:
        registro = Technique_DB( 
                # IDTech =tecnica['IDTech'],
                URL_Mitre=tecnica['URL_Mitre'],
                Name=tecnica['Name'],
                IDMitre=tecnica['IDMitre']                    
                )
        db.session.add(registro)    
        db.session.commit()  
        logging.debug('Técnica insertada...') 
        return (registro.IDTech)   
    else:
        tech = Technique_DB.query.filter_by(IDMitre = tecnica['IDMitre'] ).first()   
        return(tech.IDTech)    

# tactic's inserts
def insertar_Tactica(tactica): 
    Numregistros = 0
    Numregistros = Tactic_DB.query.filter_by(IDMitre = tactica['IDMitre'] ).count()        
    if Numregistros == 0:
        registro = Tactic_DB( 
                # IDTactic =tactica['IDTactic'],
                URL_Mitre=tactica['URL_Mitre'],
                Name=tactica['Name'],
                Description=tactica['Description'],
                IDMitre=tactica['IDMitre']                    
                )
        db.session.add(registro)    
        db.session.commit()    
        logging.debug('Tácticas insertadas...')
        return (registro.IDTactic)
    else: 
        tactic = Tactic_DB.query.filter_by(IDMitre = tactica['IDMitre'] ).first()   
        return(tactic.IDTactic)


# intel's inserts 
def insertar_Inteligencia(inteligencia):
    Numregistros = 0
    Numregistros = Inteligence_DB.query.filter_by(IDTech = inteligencia['IDTech'],IDTactic = inteligencia['IDTactic'] ).count()        
    if Numregistros == 0:
        registro = Inteligence_DB( 
                # IDIntel =inteligencia['IDIntel'],
                IDTech=inteligencia['IDTech'],
                IDTactic=inteligencia['IDTactic'],
                Function=inteligencia['Function'],
                Terminated=inteligencia['Terminated']         
                        
                )
        db.session.add(registro)    
        db.session.commit()     
        logging.debug('Inteligencia insertada...')
        return (registro.IDIntel)
    else:
        intel = Inteligence_DB.query.filter_by(IDTech = inteligencia['IDTech'],IDTactic = inteligencia['IDTactic'] ).first()        
        return (intel.IDIntel)


# task's inserts
def insertar_Tarea(tarea,IDPlan,IDIntel):
    Numregistros = 0
    Numregistros = Task_DB.query.filter_by(IDPlan = IDPlan,IDIntel = IDIntel,Orden = tarea['Orden'] ).count()        
    if Numregistros == 0:
        registro = Task_DB( 
                # IDTask =tarea['IDTask'],
                IDPlan= IDPlan,
                IDIntel=IDIntel,
                Orden=tarea['Orden']                    
                )
        db.session.add(registro)    
        db.session.commit()  
        logging.debug('Tarea insertada...')

def InsertarDatos_BD(objetos):
    Threats = objetos["Threat"]
    for Threat in Threats :
        IDThreat = insertar_Amenaza(Threat)    
    plan = objetos["Plan"]   
    IDPlan = insertar_Plan(plan[0],IDThreat)
    inteligencias = objetos["Inteligence"]   
    tecnicas = objetos["Technique"]    
    tacticas = objetos["Tactic"]
    tareas = objetos["Task"]
    for i, inteligencia in enumerate(inteligencias):
        
        IDTech = insertar_Tecnica(tecnicas[i])
        IDTactic = insertar_Tactica(tacticas[i])
        IDIntel = insertar_Inteligencia(inteligencias[i])    
        
        insertar_Tarea(tareas[i],IDPlan,IDIntel)
    
# elimina un plan pasado por post
@app.route('/deletePlan',methods=['GET', 'POST'])
def deletePlan():
    respuesta = request.json           
    IDPlan = respuesta['plan'] 
    plan = Plan_DB.query.filter_by(IDPlan = IDPlan).first() 
     
    for tarea in Task_DB.query.filter_by(IDPlan = IDPlan).all():
        Filtro = {'IDTask': tarea.IDTask }
        message =  validation_message(Directive_DB,Filtro)
        if len(message) == 0:        
            for Directive in Directive_DB.query.filter_by(IDTask = tarea.IDTask).all():
                db.session.delete(Directive)        
                Filtro = {'IDWarrior': Directive.IDWarrior }
                message =  validation_message(Warrior_DB,Filtro)
                if len(message) == 0:
                    Warrior = Warrior_DB.query.filter_by(IDWarrior = Directive.IDWarrior).first()
                    for data in DataStore_DB.query.filter_by(IDWarrior = Directive.IDWarrior).all():
                        db.session.delete(data)
                    db.session.delete(Warrior)               
        
        db.session.delete(tarea)   
 

    db.session.delete(plan)
    db.session.commit()     
    
    return redirect(url_for("plan"))

# elimina un plan pasado por post
@app.route('/implementation',methods=['GET', 'POST'])
def Implementation():
    inteligenceList = []  
    techniqueList = []     
    for inteligences in Inteligence_DB.query.filter_by(IDTactic = 'TA0001'):
        if inteligences.Function != None:
            for techniques in Technique_DB.query.filter_by(IDMitre = inteligences.IDTech):
                techniqueObj = {}      
                techniqueObj['IDMitre'] = techniques.IDMitre
                techniqueObj['Name'] = techniques.Name
                techniqueObj['Function'] = inteligences.Function
                techniqueList.append(techniqueObj)
                inteligenceObj = {}      
                inteligenceObj['IDIntel'] = inteligences.IDIntel
                inteligenceObj['Function'] = inteligences.Function
                inteligenceList.append(inteligenceObj)     
    tacticList = []      
    for tactic in Tactic_DB.query.all():
        tacticObj = {}      
        tacticObj['IDMitre'] = tactic.IDMitre
        tacticObj['Name'] = tactic.Name
        tacticList.append(tacticObj) 
    
    return render_template("implementation.html",tacticList = tacticList,techniqueList = techniqueList  )



# elimina un warrior pasado en la url
@app.route('/delWarrior/<IDWarrior>',methods=['GET', 'POST'])
def delWarrior(IDWarrior):    
    
    for Directive in Directive_DB.query.filter_by(IDWarrior = IDWarrior).all():
        db.session.delete(Directive)
        db.session.commit()       
    for data in DataStore_DB.query.filter_by(IDWarrior = IDWarrior).all():
        db.session.delete(data)
    warrior = Warrior_DB.query.filter_by(IDWarrior = IDWarrior).first()
    db.session.delete(warrior)
    db.session.commit()       
    # return json.dumps({'success':True}), 200, {'ContentType':'application/json'}     
    return redirect("/results")
#vistas principales
@app.route('/',methods=['GET', 'POST'])
def index():
    Estado = "Alive"
    if request.method == "POST":
        Estado = request.form['State']
    
    #Recuperamos los warriors
    warriorlist = []    
    datalist = {}    

    #obtenemos la fecha y hora actuales y restamos 3 min para ver si los warrior estan entre esos dos valores
    now  = datetime.datetime.now() - timedelta(minutes= 3 )    
    Filtro = {'State': 'Alive'}
    Numregistros = 0
    Numregistros = Warrior_DB.query.filter_by(**Filtro).count()        
    if Numregistros == 0:     
        message =  validation_message(Warrior_DB,Filtro)       
        logging.debug(message+ ' -- Filtro: '+ str(Filtro))
    else: 
        for warrior in Warrior_DB.query.filter_by(State = "Alive").all():        
            if str(warrior.Lastseen) < str(now): 
                warrior.State = "Dead"
                db.session.commit()            
    i = 0

    # state filter
    if Estado ==  "":
        message =  validation_messageWihoutFilter(Warrior_DB ) 
        if len(message) == 0:
            for warrior in Warrior_DB.query.all():
                warriorlist.append(warrior)
            for directiva in  Directive_DB.query.filter_by(Done= "true" , IDWarrior = warrior.IDWarrior).all() :    
                tarea = Task_DB.query.filter_by(IDTask  = directiva.IDTask).first()
                plan = Plan_DB.query.filter_by(IDPlan = tarea.IDPlan).first()
                inteligencia = Inteligence_DB.query.filter_by(IDIntel = tarea.IDIntel).first()
                tecnica = Technique_DB.query.filter_by(IDMitre = inteligencia.IDTech).first()
                i += 1
                if not warrior.IDWarrior in datalist:                
                    datalist[warrior.IDWarrior] = plan.Name + " ---> "+ tecnica.Name + " - " +str(inteligencia.Function)
                else:
                    datalist[warrior.IDWarrior] += ' | ' + tecnica.Name + " - " +str(inteligencia.Function)
    else: 
        for warrior in Warrior_DB.query.filter_by(State = Estado).all():        
            warriorlist.append(warrior)
            for directiva in  Directive_DB.query.filter_by(Done= "true" , IDWarrior = warrior.IDWarrior).all() :    

                tarea = Task_DB.query.filter_by(IDTask  = directiva.IDTask).first()
                plan = Plan_DB.query.filter_by(IDPlan = tarea.IDPlan).first()
                inteligencia = Inteligence_DB.query.filter_by(IDIntel = tarea.IDIntel).first()
                tecnica = Technique_DB.query.filter_by(IDMitre = inteligencia.IDTech).first()
                i += 1
                if not warrior.IDWarrior in datalist:                
                    datalist[warrior.IDWarrior] = plan.Name + " ---> "+ tecnica.Name + " - " +str(inteligencia.Function)
                else:
                    datalist[warrior.IDWarrior] += ' | ' + tecnica.Name + " - " +str(inteligencia.Function)                

    form = FlaskForm()        
    
    return render_template("index.html",warriorlist=warriorlist,datalist=datalist)

@app.route('/plan',methods=['GET', 'POST'])
def plan():
    form = Form()       
    planList = []      
    for plan in Plan_DB.query.all():                
        planObj = {}      
        planObj['IDPlan'] = plan.IDPlan
        planObj['Name'] = plan.Name
        planList.append(planObj)
    return render_template("plan.html", form = form, planList=planList)

@app.route('/results',methods=['GET', 'POST'])
def results():
    #Recuperamos los agents y los resultados
    warriorlist = []    
    datalist = {}
    listaDirectivasWarrior = {}
    showView = False
    sinDirectivas = False
    message = ""
    i = 0
    plan = None
    for warrior in Warrior_DB.query.all():      
        DirectivesArray = []  
        warriorlist.append(warrior)     
        Filtro = {'IDWarrior': warrior.IDWarrior}
        Numregistros = 0
        Numregistros = Directive_DB.query.filter_by(**Filtro).count()        
        if Numregistros == 0:     
            message =  validation_message(Directive_DB,Filtro)       
            logging.debug(message+ ' -- Filtro: '+ str(Filtro))
            # message = "no hay directivas para los warrior"
            sinDirectivas = True   
        else:    
            for directiva in  Directive_DB.query.filter_by( IDWarrior = warrior.IDWarrior).all() :   
                DirectivasObj = {}   
                tarea = Task_DB.query.filter_by(IDTask  = directiva.IDTask).first()            
                if plan == None:
                    plan = Plan_DB.query.filter_by(IDPlan = tarea.IDPlan).first()
                inteligencia = Inteligence_DB.query.filter_by(IDIntel = tarea.IDIntel).first()
                tecnica = Technique_DB.query.filter_by(IDMitre = inteligencia.IDTech).first()            
                DirectivasObj['techName'] = tecnica.IDMitre+" - "+ tecnica.Name
                DirectivasObj['function'] = str(inteligencia.Function)
                DirectivasObj['done'] = directiva.Done
                if (str(directiva.Good) == '0'):
                    DirectivasObj['good'] = 'Success'
                else:
                    if directiva.Done == "true":
                        DirectivasObj['good'] = 'Error'

                    else:
                        DirectivasObj['good'] = 'Pending'
                    
                DirectivesArray.append(DirectivasObj) 
                showView = True
                sinDirectivas = False
            if plan == None:
                listaDirectivasWarrior[warrior.IDWarrior] = "",DirectivesArray
            else:
                listaDirectivasWarrior[warrior.IDWarrior] = plan.Name,DirectivesArray
        
    # if showView :        
    # if listaDirectivasWarrior == None:
    #     return render_template("resultados.html",warriorlist=warriorlist)
    # else:
    return render_template("results.html",warriorlist=warriorlist,listaDirectivasWarrior = listaDirectivasWarrior)

    # else:
        # return render_template("error.html",message = message)

@app.route('/dataStore/<warriorAlias>',methods=['GET', 'POST'])
def dataStore(warriorAlias):

    Filtro = {'Alias': warriorAlias }
    message =  validation_message(Warrior_DB,Filtro)
    if len(message) != 0:
        print (message)    
        logging.debug(message+ ' -- Filtro: '+ str(Filtro))
        return render_template("error.html",message = message)           
    else:
        warrior = Warrior_DB.query.filter_by(Alias  = warriorAlias).first()
        IDWarrior = warrior.IDWarrior
        Filtro = {'IDWarrior': warrior.IDWarrior }
        message =  validation_message(Directive_DB,Filtro)
        if len(message) != 0:
            print (message)    
            logging.debug(message+ ' -- Filtro: '+ str(Filtro))       
            message = "This warrior has not loot"
            return render_template("error.html",message = message)       
        else:
            Directive = Directive_DB.query.filter_by(IDWarrior  = IDWarrior).first()
            # get IDPlan from task
            Task = Task_DB.query.filter_by(IDTask  = Directive.IDTask).first()
            IDPlan = Task.IDPlan
            Plan = Plan_DB.query.filter_by(IDPlan  =Task.IDPlan).first()
            dataStoreArray = []
            for data in  DataStore_DB.query.filter_by(IDWarrior=IDWarrior).all():
                dataStoreObj = {}  
                if data.User == None:          
                    dataStoreObj['User'] = "-"
                else:                 
                    dataStoreObj['User'] = data.User

                if data.IP == None:     
                    dataStoreObj['IP'] = "-"
                else:                 
                    dataStoreObj['IP'] = data.IP

                if data.Password == None:
                    dataStoreObj['Password'] = "-"
                else:                 
                    dataStoreObj['Password'] = data.Password

                if data.NTLM == None:
                    dataStoreObj['NTLM'] = "-"
                else:                 
                    dataStoreObj['NTLM'] = data.NTLM

                if data.LM == None:
                    dataStoreObj['LM'] = "-"
                else:                 
                    dataStoreObj['LM'] = data.LM
                dataStoreObj['IDData'] = data.IDData

                dataStoreArray.append(dataStoreObj)

    return render_template("DataStore.html", dataStoreArray = dataStoreArray, PlanName = Plan.Name)


@app.route('/addDataStore/<warriorAlias>',methods=['GET', 'POST'])
def addDataStore(warriorAlias):           
    
    Filtro = {'Alias': warriorAlias }
    message =  validation_message(Warrior_DB,Filtro)
    if len(message) != 0:
        print (message)    
        logging.debug(message+ ' -- Filtro: '+ str(Filtro))
        return render_template("error.html",message = message)             
    else:
        warrior = Warrior_DB.query.filter_by(Alias  = warriorAlias).first()
        IDWarrior = warrior.IDWarrior
        return render_template("addImplementation.html",IDWarrior = IDWarrior,Alias = warriorAlias)


@app.route('/warriors',methods=['GET', 'POST'])
def warriors():

    def existeConsola(filename):
        return os.path.isfile(filename)

    def sustituirConsola(filenameTemplate,filename,ip):
        if existeConsola('consola/consola_template'):
            f = open(filenameTemplate, "r")
            consola_template = f.read()
            f.close()
            consola = consola_template.replace("$IP",ip)
            fd = open(filename, "w")
            fd.write(consola)
            fd.close()
            return True
        return False

    filename = 'consola/consola'
    filenameTemplate = 'consola/consola_template'

    print("generar")
    if request.method == 'POST':
        ip = request.form['ip']
        if sustituirConsola(filenameTemplate,filename,ip):
            print("se ha sustituido")
            return render_template("warriors.html",ip=ip)
    return render_template("warriors.html")


@app.route('/attck',methods=['GET', 'POST'])
def threat():

    datalist = []
    for threats in Threat_DB.query.all():
        DataObj = {}
        DataObj['ID'] = threats.IDThreat
        DataObj['Name'] = threats.Name
        DataObj['Information'] = threats.Description
        datalist.append(DataObj)
    return render_template("Attck.html",threatslist=datalist)

@app.route('/ImportData',methods=['GET', 'POST'])
def ImportData():        
    return render_template("imports.html")

@app.route('/Warrior_Orders/<IDWarrior>',methods=['GET', 'POST'])
def warrior_orders(IDWarrior):    
    
    try: 
        Warrior =  Warrior_DB.query.filter_by(IDWarrior=IDWarrior).first()        
        WarriorAlias = Warrior.Alias
        PlanName = ""
        Filtro = {'IDWarrior': IDWarrior}
        message =  validation_message(Directive_DB,Filtro)
        DirectiveArray = []
        if len(message) != 0:
            print (message)    
            logging.debug(message+ ' -- Filtro: '+ str(Filtro))
            # return "false"
        else:
            Directives = Directive_DB.query.filter_by(IDWarrior=IDWarrior).all()
            logging.debug("IDwarrior: "+ IDWarrior)
            

            for directive in Directives:
                dirObj = {}        
                dirObj['IDWarrior'] = directive.IDWarrior
                dirObj['IDTask'] = directive.IDTask
                dirObj['Result'] = directive.Result
                dirObj['Done'] = directive.Done
                dirObj['Good'] = directive.Good
                if (str(directive.Good) == '0'):
                    dirObj['Good'] = 'Success'
                else:
                    if directive.Done == "true":
                        dirObj['Good'] = 'Error'
                    else:
                        dirObj['Good'] = 'Pending'
                    


                Task =  Task_DB.query.filter_by(IDTask=directive.IDTask).first()                
                Intel =  Inteligence_DB.query.filter_by(IDIntel=Task.IDIntel).first()                
                Tech =  Technique_DB.query.filter_by(IDMitre=Intel.IDTech).first()                        
                dirObj['TechName'] = Tech.IDMitre +" - "+ Tech.Name   +" - "+ Intel.Function    
                Plan =  Task_DB.query.filter_by(IDTask =directive.IDTask).first()       
                Plan =  Plan_DB.query.filter_by(IDPlan =Plan.IDPlan).first()       
                PlanName = Plan.Name
                DirectiveArray .append(dirObj)           
        form = Form()                     
        return render_template("Warrior_Orders.html", form = form,Directivelist = DirectiveArray,warrior = WarriorAlias, Plan = PlanName.rstrip())
    except Exception as e:
        return render_template("error.html",message = e)  
        

   

    
@app.route('/set_data',methods=['GET', 'POST'])
def set_data():        

    IDWarrior = request.form['IDWarrior']
    User = request.form['User']
    if User == "":
        User = None
    Password = request.form['Password']
    if Password == "":
        Password = None
    IP = request.form['IP']
    if IP == "":
        IP = None
    NTLM = request.form['NTLM']
    if NTLM == "":
        NTLM = None
    LM = request.form['LM']
    if LM == "":
        LM = None

    registro = DataStore_DB(                         
                IDWarrior= IDWarrior,
                Password = Password,
                User = User,
                IP = IP,
                NTLM = NTLM,
                LM = LM
                )
    db.session.add(registro)    
    db.session.commit() 
    return redirect(url_for("results"))

@app.route('/putdata',methods=['POST'])
def putData():
    if 'id' in request.form.keys():
        warriorAlias = request.form['id']
        Filtro = {'Alias': warriorAlias }
        message =  validation_message(Warrior_DB,Filtro)
        if len(message) != 0:
            print (message)    
            logging.debug(message+ ' -- Filtro: '+ str(Filtro))
            return "false"            
        else:
            warrior = Warrior_DB.query.filter_by(Alias  = warriorAlias).first()
            Directive = Directive_DB.query.filter_by(IDWarrior  = warrior.IDWarrior).first()
            # get IDPlan from task
            Task = Task_DB.query.filter_by(IDTask  = Directive.IDTask).first()
            IDPlan = Task.IDPlan
            User = None
            IP = None
            Password = None
            NTLM = None
            LM = None

            if 'user' in request.form.keys():
                User = request.form['user']
            if 'ip' in request.form.keys():
                IP = request.form['ip']
            if 'pass' in request.form.keys():  
                Password = request.form['pass']
            if 'ntlm' in request.form.keys():  
                NTLM = request.form['ntlm']
            if 'lm' in request.form.keys():  
                LM = request.form['lm']

            registro = DataStore_DB(                         
                IDWarrior= warrior.IDWarrior,
                Password = Password,
                User = User,
                IP = IP,
                NTLM = NTLM,
                LM = LM
                )

            db.session.add(registro)    
            db.session.commit()   
        
     
    return "200"

@app.route('/getdata',methods=['POST'])
def getData():
    dataStoreArray = [] 
    if 'id' in request.form.keys():
        warriorAlias = request.form['id']
        Filtro = {'Alias': warriorAlias }
        message =  validation_message(Warrior_DB,Filtro)
        if len(message) != 0:
            print (message)    
            logging.debug(message+ ' -- Filtro: '+ str(Filtro))
            return "false"            
        else:
            warrior = Warrior_DB.query.filter_by(Alias  = warriorAlias).first()
            Directive = Directive_DB.query.filter_by(IDWarrior  = warrior.IDWarrior).first()
            # get IDPlan from task
            Task = Task_DB.query.filter_by(IDTask  = Directive.IDTask).first()
            IDPlan = Task.IDPlan  
            
            for data in  DataStore_DB.query.filter_by(IDWarrior= warrior.IDWarrior).all():
                dataStoreObj = {}
                add = True
                if 'ip' in request.form.keys() and add:
                    if data.IP != None:                    
                        add = True 
                        dataStoreObj['IP'] = data.IP 
                    else:      
                        add = False 
                if 'password' in request.form.keys() and add:               
                    if data.Password != None:                    
                        add = True 
                        dataStoreObj['Password'] = data.Password 
                    else:      
                        add = False 
                if 'user' in request.form.keys() and add:                
                    if data.User != None:                    
                        add = True 
                        dataStoreObj['User'] = data.User
                    else:      
                        add = False 
                if 'ntlm' in request.form.keys() and add:
                    if data.NTLM != None:                    
                        add = True 
                        dataStoreObj['NTLM'] = data.NTLM 
                    else:      
                        add = False 
                if 'lm' in request.form.keys() and add:
                    if data.LM != None:                    
                        add = True 
                        dataStoreObj['LM'] = data.LM 
                    else:      
                        add = False 
                if add: 
                    dataStoreArray.append(dataStoreObj)
            
        return jsonify({'DataStore': dataStoreArray})

@app.route('/exportar',methods=['GET', 'POST'])
def exportar():  
    IDPlan = request.form['IDPlan']
    plan = Plan_DB.query.filter_by(IDPlan = IDPlan).first()  
    NamePlan = plan.Name   
    PlanArray = []
    PlanObj = {}    
    PlanObj['IDPlan']                   = plan.IDPlan  
    PlanObj['Name']                     = plan.Name  
    PlanObj['Description']              = plan.Description  
    PlanArray.append(PlanObj)
    ThreatArray = []
    ThreatObj = {}
    Threat = Threat_DB.query.filter_by(IDThreat = plan.IDThreat).first()            
    ThreatObj['IDThreat']               = Threat.IDThreat  
    ThreatObj['Created']                = Threat.Created  
    ThreatObj['Modified']               = Threat.Modified  
    ThreatObj['Name']                   = Threat.Name  
    ThreatObj['Description']            = Threat.Description  
    ThreatObj['Windows']                = Threat.Windows   
    ThreatObj['MacOS']                  = Threat.MacOS   
    ThreatObj['Linux']                  = Threat.Linux  
    ThreatArray.append(ThreatObj)
    Tasks = Task_DB.query.filter_by(IDPlan=plan.IDPlan).all()
    TaskArray = []
    IntelArray = []
    TacticArray = []
    TechArray = []
    for task in Tasks:        
        taskObj = {}
        taskObj['IDTask']               = task.IDTask  
        taskObj['IDPlan']               = task.IDPlan  
        taskObj['IDIntel']              = task.IDIntel 
        taskObj['Orden']                = task.Orden   
        TaskArray.append(taskObj)        
        inteligencia = Inteligence_DB.query.filter_by(IDIntel = task.IDIntel).first()
        IntelObj = {}
        IntelObj['IDIntel']             = inteligencia.IDIntel           
        IntelObj['IDTech']              = inteligencia.IDTech    
        IntelObj['IDTactic']            = inteligencia.IDTactic  
        IntelObj['Function']            = inteligencia.Function  
        IntelObj['Terminated']          = inteligencia.Terminated
        IntelArray.append(IntelObj)   
        Tecnica = Technique_DB.query.filter_by(IDMitre = inteligencia.IDTech).first()
        TecnicaObj = {}
        TecnicaObj['IDTech']            = Tecnica.IDTech           
        TecnicaObj['URL_Mitre']         = Tecnica.URL_Mitre           
        TecnicaObj['Name']              = Tecnica.Name           
        TecnicaObj['IDMitre']           = Tecnica.IDMitre
        TechArray.append(TecnicaObj)
        Tactica = Tactic_DB.query.filter_by(IDMitre = inteligencia.IDTactic).first()        
        TacticObj = {}
        TacticObj['IDTactic']           = Tactica.IDTactic           
        TacticObj['URL_Mitre']          = Tactica.URL_Mitre           
        TacticObj['Name']               = Tactica.Name           
        TacticObj['Description']        = Tactica.Description           
        TacticObj['IDMitre']            = Tactica.IDMitre     
        TacticArray.append(TacticObj)                

    exportacionObj  = {}
    exportacionObj["Plan"] = PlanArray
    exportacionObj["Threat"] = ThreatArray
    exportacionObj["Task"] = TaskArray
    exportacionObj["Inteligence"] = IntelArray
    exportacionObj["Technique"] = TechArray
    exportacionObj["Tactic"] = TacticArray                
    
    
    NamePlan = NamePlan.replace(" ", "_")
    return Response(json.dumps(exportacionObj, indent=3), 
        mimetype='application/json',
        headers={'Content-Disposition':'attachment;filename='+NamePlan+'.json'})

@app.route('/ins_directive',methods=['POST'])
def Ins_Directive():  
    form = Form()                     
    IDTasks = request.form.getlist('IDTasks[]')
    IDWarrior = request.form['warrior']
    for IDTask in IDTasks :
        registro = Directive_DB(             
            IDTask = IDTask,
            IDWarrior=IDWarrior,
            Done = "false"
            )    
        db.session.add(registro)    
        db.session.commit()    
    return redirect("Warrior_Orders/"+IDWarrior)
      
@app.route('/sel_plan_/<IDPlan>',methods=['GET', 'POST'])
def selplan(IDPlan):    
    form = Form()
    Tasks = Task_DB.query.filter_by(IDPlan=IDPlan).all()
    TaskArray = [] 
    for task in Tasks:
        taskObj = {}        
        taskObj['IDTask'] = task.IDTask
        intel = Inteligence_DB.query.filter_by(IDIntel = task.IDIntel).first()    
        tech = Technique_DB.query.filter_by(IDMitre = intel.IDTech).first()    
        tactic = Tactic_DB.query.filter_by(IDMitre = intel.IDTactic).first()  
        taskObj['IDMitreTech'] = tech.IDMitre
        taskObj['NameTech'] = tech.Name
        taskObj['IDMitreTactic'] = tactic.IDMitre
        taskObj['NameTactic'] = tactic.Name
        taskObj['Function'] = intel.Function
        plan = Plan_DB.query.filter_by(IDPlan = IDPlan).first()    
        taskObj['Plan'] = plan.Name
        TaskArray.append(taskObj)       

    plan = Plan_DB.query.filter_by(IDPlan = IDPlan).first()  
    warriorList = []      
    for warrior in Warrior_DB.query.filter_by(State= "Alive" ).all():
        warriorObj = {}      
        warriorObj['IDWarrior'] = warrior.IDWarrior
        warriorObj['Alias'] = warrior.Alias
        warriorList.append(warriorObj)
    planName = plan.Name

    return render_template("task.html",form = form ,warriorList = warriorList, Tasklist = TaskArray ,plan = planName.rstrip(),planDescription =plan.Description , idplan = plan.IDPlan)

@app.route('/import_plan_json',methods=['POST'])
def Parsing():

    contenido = request.form["content-file"]    
    objetos = json.loads(contenido)
    InsertarDatos_BD(objetos)   
    return redirect("/")
    

  

@app.route('/Directive#Tactica/<IDTactic>',methods=['GET', 'POST'])
def Tecnica(Tactica):        
    con = sqlite3.connect('mydatabase.db')
    cursorObj = con.cursor()
    cursorObj.execute("SELECT IDTech,URL_Mitre,Name,IDMitre from Technique WHERE IDTactic = ?" ,(IDTactic))
    records = cursorObj.fetchall()
    Techlist = []
    for row in records:
        w = technique(row[0],row[1],row[2],row[3])
        Techlist.append(w)
    return jsonify({'techniques' : Techlist})

def Tactica(): 
    con = sqlite3.connect('mydatabase.db')
    cursorObj = con.cursor()
    cursorObj.execute("SELECT IDTactic,URL_Mitre,Name,Description, IDMitre from Tactic ")
    records = cursorObj.fetchall()
    Tacticlist = []
    for row in records:
        w = Tactic(row[0],row[1],row[2],row[3],row[4])
        Tacticlist.append(w)
        
    return Tacticlist

@app.route('/Directive',methods=['GET', 'POST'])    
def Directive():
    form = Form() 

    inteligenceList = []  
    techniqueList = []     
    for inteligences in Inteligence_DB.query.filter_by(IDTactic = 'TA0001'):
        if inteligences.Function != None:
            for techniques in Technique_DB.query.filter_by(IDMitre = inteligences.IDTech):
                techniqueObj = {}      
                techniqueObj['IDMitre'] = techniques.IDMitre
                techniqueObj['Name'] = techniques.Name
                techniqueObj['Function'] = inteligences.Function
                techniqueList.append(techniqueObj)
                inteligenceObj = {}      
                inteligenceObj['IDIntel'] = inteligences.IDIntel
                inteligenceObj['Function'] = inteligences.Function
                inteligenceList.append(inteligenceObj)     
    tacticList = []      
    for tactic in Tactic_DB.query.all():
        tacticObj = {}      
        tacticObj['IDMitre'] = tactic.IDMitre
        tacticObj['Name'] = tactic.Name
        tacticList.append(tacticObj)

    form.threat.choices= [ (threat.IDThreat,threat.Name) for threat in Threat_DB.query.all() ]
    threatList = []      
    for threat in Threat_DB.query.all():
        threatObj = {}      
        threatObj['IDThreat'] = threat.IDThreat
        threatObj['Name'] = threat.Name
        threatList.append(threatObj)
        
    return render_template("Directive.html",
                            form = form,
                            inteligenceList = inteligenceList,
                            techniqueList = techniqueList,
                            tacticList = tacticList,
                            threatList = threatList)

@app.route ('/Directive/tactic/<IDIntel>')
def inteligence (IDIntel):    
    intels = Inteligence_DB.query.filter_by(IDTactic=IDIntel).all()
    intelArray = [] 
    for intel in intels:
        if intel.Function != None:
            intelObj = {}
            intelObj['IDIntel'] = intel.IDIntel
            tech = Technique_DB.query.filter_by(IDMitre = intel.IDTech).first()   
            intelObj['IDMitre'] = tech.IDMitre 
            intelObj['Name'] = tech.Name
            intelObj['Function'] = intel.Function
            intelArray.append(intelObj)

    return jsonify({'intels': intelArray})

@app.route('/givemetable',methods=['GET', 'POST'])
def givemetable():

    datalist = []
    if request.method == 'POST':    
        response =  json.loads(request.data)        
        Data = response['Datos']         
        if 'Threats' in Data:          
            for threats in Threat_DB.query.all():
                DataObj = {}
                DataObj['ID'] = threats.IDThreat
                DataObj['Name'] = threats.Name
                DataObj['Information'] = threats.Description
                datalist.append(DataObj)
        if 'Tactics' in Data:     
            for tactics in Tactic_DB.query.all():
                DataObj = {}
                DataObj['ID'] = tactics.IDMitre
                DataObj['Name'] = tactics.Name
                DataObj['Information'] = tactics.URL_Mitre
                datalist.append(DataObj)
        
        if 'Techniques' in Data:     
            for tech in Technique_DB.query.all():                
                DataObj = {}
                DataObj['ID'] = tech.IDMitre
                DataObj['Name'] = tech.Name
                DataObj['Information'] = tech.URL_Mitre
                datalist.append(DataObj)
    
    return jsonify(datalist)
@app.route('/givemefile/<fileName>',methods=['GET', 'POST'])

def givemefile(fileName):
    
    path = "functions/"+fileName     
    f = open(path)
    data = f.read()
    f.close()      

    res = make_response(jsonify({"file": data}), 200)

    return res
@app.route('/log/<idwarrior>/<nombrefuncion>',methods=['GET'])
def log(idwarrior,nombrefuncion):
    #Recuperamos resultados de este warrior y de la funcion
    con = sqlite3.connect('mydatabase.db')
    cursorObj = con.cursor()
    cursorObj.execute("SELECT result FROM Directive WHERE idwarrior = ? AND IDTask = ? LIMIT 1",(idwarrior,nombrefuncion))
    records = cursorObj.fetchall()
    for row in records:
        return str(row[0].encode("utf-8"))

@app.route('/consola',methods=['GET', 'POST'])
def consola():
    def existeConsola(filename):
        return os.path.isfile(filename)

    def leerFichero(filename):
        f = open(filename, "r")
        consola = f.read()
        return consola

    filename = 'consola/consola'
    if existeConsola(filename):
        scheduler = leerFichero(filename)
        return scheduler.encode("utf-8")
    return ""

@app.route('/getplan',methods=['POST'])
def getplan():    
    AliasWarrior = request.form['id'] #  warrior Alias
    DirectivesArray = []    
    
    DirectivasObj = {} 

    Filtro = {'Alias': AliasWarrior }
    message =  validation_message(Warrior_DB,Filtro)
    if len(message) != 0:
        print (message)    
        logging.debug(message+ ' -- Filtro: '+ str(Filtro))
        return "false"            
    else:
        warrior = Warrior_DB.query.filter_by(Alias  = AliasWarrior).first()
        warrior.Lastseen = datetime.datetime.now()
        db.session.commit()     
        rows = 0
        rows = Directive_DB.query.filter_by(Done = "false" , IDWarrior = warrior.IDWarrior).count()    
        if rows > 0:            
            logging.debug('hay plan para el alias: '+ AliasWarrior)
            return "true"
        else:
            logging.debug('no hay plan para el alias: '+AliasWarrior )
            return "false"

@app.route('/givemeplan',methods=['POST'])
def givemeplan():   
    #Debemos recibir IDPlan, IDWarrior y nombre funcion
    AliasWarrior = request.form['id'] # Alias del warrior
    DirectivesArray = []    
    
    DirectivasObj = {} 
    Filtro = {'Alias': AliasWarrior, 'State' : 'Alive' }
    message =  validation_message(Warrior_DB,Filtro)
    if len(message) != 0:
        print (message)    
        logging.debug(message+ ' -- Filtro: '+ str(Filtro))
        return "error"            
    else:
        warrior = Warrior_DB.query.filter_by(Alias  = AliasWarrior,State = "Alive").first()
        i = 0 
        for directiva in  Directive_DB.query.filter_by(Done= "false" , IDWarrior = warrior.IDWarrior).all() :    
            tarea = Task_DB.query.filter_by(IDTask  = directiva.IDTask).first()
            plan = Plan_DB.query.filter_by(IDPlan = tarea.IDPlan).first()
            inteligencia = Inteligence_DB.query.filter_by(IDIntel = tarea.IDIntel).first()            
            dead =  0                
            Tarea = {}
            if inteligencia.Terminated == "False":
                dead = 1
            else: 
                dead = 0                    
            Tarea['Function'] = str(inteligencia.Function)
            Tarea['IDFunction'] = str(directiva.IDDirective)
            Tarea['Die'] = str(dead)
            DirectivasObj["t"+str(i)] = Tarea      
            i =  i + 1        

        return jsonify(plan=plan.IDPlan,id=warrior.Alias,tasks= DirectivasObj,ntasks=i)

@app.route('/givemetask',methods=['POST'])
def givemetask():

    def leerFichero(fichero):
        path = "functions/"+fichero
        logging.debug('Ruta del fichero: '+ path)        
        f = open(path)
        data = f.read()
        f.close()        
        return data
        #return data.encode("UTF-8")

    #Debemos recibir IDPlan, IDWarrior y nombre funcion
    idwarrior = request.form['id']
    logging.debug('Warrior Alias: '+ idwarrior)    
    idplan = request.form['plan']
    logging.debug('plan ID: '+ idplan)
    funcion = request.form['funcion']
    logging.debug('Function Name: '+ funcion)    

    return jsonify(plan=idplan,id=idwarrior,funcion=leerFichero(funcion))
    
@app.route('/givemepending',methods=['POST'])
def givemepending():

    def leerFichero(fichero):
        path = "functions/"+fichero
        f = open(path)
        data = f.read()
        f.close()
        return data.encode("UTF-8")

    AliasWarrior = request.args['id'] # Alias del warrior
    DirectivesArray = []    
    
    DirectivasObj = {} 
    Filtro = {'Alias': AliasWarrior}
    message =  validation_message(Warrior_DB,Filtro)
    if len(message) != 0:
        print (message)    
        logging.debug(message+ ' -- Filtro: '+ str(Filtro))
        return "error"            
    else:
        warrior = Warrior_DB.query.filter_by(Alias  = AliasWarrior).first()
        i = 0 
        for directiva in  Directive_DB.query.filter_by(Done= "false" , IDWarrior = warrior.IDWarrior).all() :    
            tarea = Task_DB.query.filter_by(IDTask  = directiva.IDTask).first()
            plan = Plan_DB.query.filter_by(IDPlan = tarea.IDPlan).first()
            inteligencia = Inteligence_DB.query.filter_by(IDIntel = tarea.IDIntel).first()            
            dead =  0                
            Tarea = {}
            if inteligencia.Terminated == "False":
                dead = 1
            else: 
                dead = 0                    
            Tarea['Function'] = str(inteligencia.Function)
            Tarea['Die'] = str(dead)
            DirectivasObj["t"+str(i)] = Tarea      
            i =  i + 1        

        return jsonify(plan=plan.IDPlan,id=warrior.Alias,tasks= DirectivasObj,ntasks=i)

@app.route('/putresult',methods=['POST'])
def putresult():
    AliasWarrior = request.form['id']
    idplan = request.form['plan']
    resultado = request.form['resultado']
    funcion = request.form['funcion']
    IDDirective = request.form['idfunction']
    good = request.form['good']
    if(len(resultado)>0):

        Filtro = {'Alias': AliasWarrior, 'State' : 'Alive' }
        message =  validation_message(Warrior_DB,Filtro)
        if len(message) != 0:
            print (message)   
            logging.debug(message+ ' -- Filtro: '+ str(Filtro))
            return "error"            
        else:
            warrior =  Warrior_DB.query.filter_by(Alias = AliasWarrior,State = "Alive").first()        
            IDWarrior = warrior.IDWarrior
            Filtro = {'IDWarrior': IDWarrior, 'IDDirective' : IDDirective }
            message =  validation_message(Directive_DB,Filtro)
            if len(message) != 0:
                print (message)    
                logging.debug(message+ ' -- Filtro: '+ str(Filtro))
                return "error"            
            else:
                Directiva = Directive_DB.query.filter_by(IDWarrior= IDWarrior,IDDirective = IDDirective).first()        
                Directiva.Result = resultado
                Directiva.Good= good
                Directiva.Done = "true"
                db.session.commit()   
    return "200"

@app.route('/hi',methods=['POST'])
def hi():

    #Recibimos datos de warrior (id + info sistema)
    idwarrior = request.form['id']    
    logging.debug('Alias warrior hi 1: '+idwarrior)
    name = request.form['name']
    arch = request.form['arch']
    machine = request.form['machine']
    pid = request.form['pid']
    time = datetime.datetime.now()
    ip = request.remote_addr
    registro = Warrior_DB(                 
                State = "Alive",
                Legacy = "",
                Alias = idwarrior,
                Os = name,
                Arch = arch, 
                Name = machine,
                PID = pid,
                Lastseen = time,
                IP = ip            
            )    
    db.session.add(registro)    
    db.session.commit()  
    return "200"
@app.route('/hi2',methods=['POST'])
def hi2():

    AliasWarrior = request.form['id']
    logging.debug('Alias warrior hi 2: '+AliasWarrior)
    
    Filtro = {'Alias': AliasWarrior, 'State' : 'Alive' }
    message =  validation_message(Warrior_DB,Filtro)
    if len(message) != 0:
        print (message)   
        logging.debug(message+ ' -- Filtro: '+ str(Filtro))
        return "error"            
    else:
        warrior =  Warrior_DB.query.filter_by(Alias = AliasWarrior,State = "Alive").first()
        warrior.State = "Dead"
        OldIDWarrior = warrior.IDWarrior
        db.session.commit()   
        name = request.form['name']
        arch = request.form['arch']
        machine = request.form['machine']
        pid = request.form['pid']
        time = datetime.datetime.now()
        ip = request.remote_addr    
        registro = Warrior_DB(                 
                    State = "Alive",
                    Legacy = AliasWarrior,
                    Alias = AliasWarrior,
                    Os = name,
                    Arch = arch, 
                    Name = machine,
                    PID = pid,
                    Lastseen = time,
                    IP = ip            
                )    
        db.session.add(registro)    
        db.session.commit()  
        IDWarrior = registro.IDWarrior
        for Directiva in Directive_DB.query.filter_by(IDWarrior = OldIDWarrior,Done = "false").all():
            Directiva.IDWarrior = IDWarrior
            db.session.commit()           
        return "200"

@app.route('/bye',methods=['POST'])
def bye():
    AliasWarrior = request.form['id']
    Warrior = Warrior_DB.query.filter_by(Alias = AliasWarrior,State = 'Alive').first()
    Warrior.State = "Dead"
    db.session.commit()  
    return "200"

    
@app.route('/settaskplan',methods=['POST'])
def AsentarPlan():  
  
    # form = Form_validations(request.form["ThreatName"])
    # if form.validate():
    
    tareas = request.form["TaskList"]
    ThreatName = request.form["ThreatName"]
    ThreatDesc = request.form["ThreatDesc"]
    if ThreatName == "":   
        error = "Cannot insert a threat without name"     
        return render_template('error.html',message = error)    
    if tareas == "":   
        error = "Cannot insert a threat without tasks"     
        return render_template('error.html',message = error)
    PlanName = ThreatName
    PlanDesc = ThreatDesc
    registro = Threat_DB(          
    Created                  = datetime.datetime.now(),
    Modified                 = datetime.datetime.now(),
    Name                     = ThreatName,
    Description              = ThreatDesc,
    Windows                  = "true"    
    )   
    db.session.add(registro)    
    db.session.commit()        
    IDThreat = registro.IDThreat

    registro = Plan_DB( 
            IDThreat=IDThreat,
            Name=PlanName,
            Description=PlanDesc
            )    

    db.session.add(registro)    
    db.session.commit()        
    idplan = registro.IDPlan
    objeto =  tareas.split('\r\n')
    Tareas =  []
    i = 1
    for obj in objeto:        
        posini = 8        
        posfinal =  obj.find("Nombre:")        
        id = obj[posini:posfinal].strip()                
        if id != "":
            registro2 = Task_DB( 
                        IDPlan=idplan,
                        IDIntel=id,
                        Orden= i
                        )    
            db.session.add(registro2)    
            db.session.commit()        
            i +=1
    return redirect(url_for("plan"))
    # else: 
    # return render_template('Directive.html',)

@app.route('/createtables',methods=['GET','POST'])
def createtables():
    con = sqlite3.connect('mydatabase.db')
    cursorObj = con.cursor()
    cursorObj.execute('CREATE TABLE warrior(idwarrior text PRIMARY KEY, os text, arch text, name text,pid text, lastseen text, ip text)')
    cursorObj.execute('CREATE TABLE plan(idplan text PRIMARY KEY, idwarrior text, idtask text, task text, resultado text, done text)')
    con.commit()
    return "OK"
@app.route('/reset',methods=['GET','POST'])
def reset():
    for records in DataStore_DB.query.all():
        db.session.delete(records)
    for records in Directive_DB.query.all():
        db.session.delete(records)
    for records in Warrior_DB.query.all():
        db.session.delete(records)
    for records in Task_DB.query.all():
        db.session.delete(records)
    for records in Plan_DB.query.all():
        db.session.delete(records)
    db.session.commit()  

    con = sqlite3.connect('mydatabase.db')
    cursorObj = con.cursor()
    cursorObj.execute('DELETE FROM Threat where IDThreat > 278')
    con.commit()

    return redirect("/")


@app.route('/deletetables',methods=['GET','POST'])
def deletetables():
    con = sqlite3.connect('mydatabase.db')
    cursorObj = con.cursor()
    cursorObj.execute('DELETE from warrior')
    cursorObj.execute('DELETE FROM Task')
    con.commit()
    return "OK"



@app.errorhandler(403)
def not_found_error(error):
    return render_template('error.html',message = error), 403

@app.errorhandler(400)
def not_found_error(error):
    return render_template('error.html',message = error), 400 

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html',message = error), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html',message = error), 500


if __name__ == '__main__':    

    # app.run(host="10.10.200.1", port=5000,debug=True)
    app.run(host="0.0.0.0", port=5000,debug=False)
    
