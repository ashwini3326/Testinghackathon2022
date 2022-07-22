from flask import Flask, render_template, request, redirect, jsonify
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_wtf import FlaskForm
import requests
import os
import json
import urllib.request
from urllib.request import urlretrieve
import pandas as pd
import subprocess
import lineage

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

class LoginForm(FlaskForm):

	email = StringField('Email')
	password = PasswordField('Password')
	remember = BooleanField('Remember Me')
	submit = SubmitField('Login')
    
def get_dags_values_from_table(selected_table):
    
    csvFile = pd.read_csv(os.path.join('static', 'input', 'dag_parsed_output.csv'))
    dagsList = []
    
    for i in range(len(csvFile)):
        
        target = csvFile.iloc[i]['target']
        dag_id = csvFile.iloc[i]['dag_id']
        
        if target == selected_table:
            dagsList.append(dag_id)
    
    return list(set(dagsList))

def get_control_m_values(selected_table):

    """
    dummy function, replace with e.g. database call. If data not change, this function is not needed but dictionary
    could be defined globally
    """
    csvFile = pd.read_csv(os.path.join('static', 'input', 'dag_parsed_output.csv'))
    ctmList = []
    
    for i in range(len(csvFile)):
        
        target = csvFile.iloc[i]['target']
        controlm_job_name = csvFile.iloc[i]['controlm_job_name']
        
        if target == selected_table:
            ctmList.append(controlm_job_name)

    return list(set(ctmList))
    
def get_dags_values(selected_ctm):

    csvFile = pd.read_csv(os.path.join('static', 'input', 'dag_parsed_output.csv'))
    dagsList = []
    
    for i in range(len(csvFile)):
        
        
        controlm_job_name = csvFile.iloc[i]['controlm_job_name']
        dag_id = csvFile.iloc[i]['dag_id']
        
        if controlm_job_name == selected_ctm:
            dagsList.append(dag_id)
    
    return list(set(dagsList))


@app.route('/_update_ctm_dropdown')
def update_ctm_dropdown():

    # the value of the first dropdown (selected by the user)
    selected_table = request.args.get('selected_table', type=str)
    
    # get values for the second dropdown
    if selected_table == "":
        updated_values = []
    else:
        updated_values = get_control_m_values(selected_table)

    # create the value sin the dropdown as a html string
    #html_string_selected = '<option value="" disabled selected>Control-M Job</option>'
    html_string_selected = '<option value="Control-M Job">Control-M Job</option>'
    for entry in updated_values:
        html_string_selected += '<option value="{}">{}</option>'.format(entry, entry)

    return jsonify(html_string_selected=html_string_selected)
    
@app.route('/_update_dags_dropdown')
def update_dags_dropdown():

    # the value of the first dropdown (selected by the user)
    selected_ctm = request.args.get('selected_ctm', type=str)
    
    # get values for the second dropdown
    if selected_ctm == "":
        updated_values = []
    else:
        updated_values = get_dags_values(selected_ctm)
    
    # create the value sin the dropdown as a html string
    #html_string_selected = '<option value="" disabled selected>Composer Dag</option>'
    html_string_selected = '<option value="Composer Dag">Composer Dag</option>'
    for entry in updated_values:
        html_string_selected += '<option value="{}">{}</option>'.format(entry, entry)

    return jsonify(html_string_selected=html_string_selected)

@app.route('/')
@app.route('/index')
def main():
    return render_template('index.html')
 
@app.route('/generateTableLineage', methods=['GET', 'POST'])
def generateTableLineage():
    form = LoginForm()
    
    #class_entry_relations = get_control_m_values()
    #
    #default_classes = []
    #default_values = class_entry_relations[default_classes[0]]
    #print(default_classes, default_values)
    if request.method == "POST":
        
        lineageTableName = request.form.get('lineageTableName')
        lineageLevel = request.form.get('lineageLevel')
        ctmName = request.form.get('all_ctm')
        dagName = request.form.get('all_dags')
        
        try:
            if ctmName == "Control-M Job" or dagName == "Composer Dag":
                dags_list = get_dags_values_from_table(lineageTableName)
                result_type, tableLineageTree = lineage.generateAllLineage(dags_list, lineageTableName, lineageLevel)
                ctmName = "All Control-M Jobs"
                dagName = "All Composer Dags"
            else:
                result_type, tableLineageTree = lineage.generateLineage(ctmName, dagName, lineageTableName, lineageLevel)
            if result_type == "CACHE_GENERATED":
                msg = f"Lineage found in cache storage! Displaying cached Table Lineage for : {lineageTableName} and Degree : {lineageLevel} and Control-M Job Name : {ctmName} and Dag Name : {dagName}"
            elif result_type == "NO_LINEAGE_GENERATED":
                msg = f"Table Lineage doesn't exists for : {lineageTableName} as no source details found!"
            else:
                msg = f"Lineage not found in cache storage! Generated Table Lineage for : {lineageTableName} and Degree : {lineageLevel}  and Control-M Job Name : {ctmName} and Dag Name : {dagName}"
            return render_template('generateTableLineage.html', form=form, msg = msg, displayData = tableLineageTree, all_classes=[],all_entries=[])
        except Exception as e:
            return render_template('failure.html', failure_msg = f"Error while Generating Lineage : {str(e)}; If you think it's a mistake, please contact admin!")
    
    return render_template('generateTableLineage.html', form=form, all_ctm=[],all_dags=[])
    
@app.route('/refreshDataSource', methods=['GET', 'POST'])
def refreshDataSource():
    form = LoginForm()
    
    if request.method == "POST":
        
        dagParsedOutputTable = request.form.get('dagParsedOutputTable')
        
        try:
            return_code, msg = lineage.download_dag_parsed_output(dagParsedOutputTable)
            return render_template('refreshDataSource.html', form=form, msg = msg)
        except Exception as e:
            return render_template('failure.html', failure_msg = f"Error while refreshing Lineage Data Source Table : {str(e)}; If you think it's a mistake, please contact admin!")
    
    return render_template('refreshDataSource.html', form=form)
   
"""
@app.route('/logs', methods=['GET', 'POST'])
def displayLogs():
    form = LoginForm()
    if request.method == "POST":
        logFilePathToDisplay = request.form.get('logFilePath')
        try:
            with open(logFilePathToDisplay) as displayDataFile:
                displayData = displayDataFile.read()
            displayDataFile.close()
            
            return render_template('logs.html', form=form, logPath = logFilePathToDisplay, displayData = displayData)
        except:
            return render_template('failure.html', failure_msg = "Log File path not found on 001 edge node; If you think it's a mistake, please contact admin!")
    return render_template('logs.html', form=form)
    
@app.route('/incrLoadForm', methods=['GET', 'POST'])
def incrLoadInput():
    form = LoginForm()
    if request.method == 'POST':
        db2_schema = request.form.get('db2_schema')
        db2_table = request.form.get('db2_table')
        bq_project = request.form.get('bq_project')
        bq_dataset = request.form.get('bq_dataset')
        bq_table = request.form.get('bq_table')
        delimeter = request.form.get('delimeter')
        split_by_column = request.form.get('split_by_column')
        no_of_mappers = request.form.get('no_of_mappers')
        post_processing_cmd = request.form['post_processing_cmd']
        alert_email = request.form.get('alert_email')
        
        filter_cond = request.form.get('filter_cond')
        
        target_table_name = bq_project + "." + bq_dataset + "." + bq_table
        
        json_to_find = db2_schema.strip().lower() + "_" + db2_table.strip().lower() + "_hist_copy_full_load.json"
        
        if db2_schema.strip().lower() + "." + db2_table.strip().lower() in db2_tables_list:
            if json_to_find in db2_jsons_list:
                
                with open("/localstorage2/temp/zsdt/static/input/counts/"+db2_schema.strip().lower()+"_"+db2_table.strip().lower()+"_count.txt") as countFile:
                    run_count = int(countFile.read())
                countFile.close()
                next_run_count_value = run_count + 1
                
                logFile = "/localstorage2/temp/zsdt/logs/" + db2_schema.strip().lower()+"_"+db2_table.strip().lower()+"_" + str(run_count+1) + "_full_load.log"
                
                with open("/localstorage2/temp/zsdt/static/input/jsons/"+json_to_find) as jsonFile:
                    jsonData = json.load(jsonFile)
                jsonData["TARGET_TABLE_NAME"] = target_table_name
                
                if delimeter.strip() != '':
                    jsonData["DELIMITER"] = delimeter
                if split_by_column.strip() != '':
                    jsonData["SPLIT_BY_COL"] = split_by_column
                if no_of_mappers.strip() != '':
                    jsonData["NUM_MAPPERS"] = no_of_mappers
                    
                if filter_cond.strip() != '':
                    filter_cond = "("+filter_cond+") and "
                    initial_query = jsonData["QUERY"]
                    final_query = initial_query.replace("\\$CONDITIONS", filter_cond+"\\$CONDITIONS")
                    jsonData["QUERY"] = final_query
                
                
                with open("/localstorage2/temp/zsdt/static/output/jsons/"+json_to_find, "w") as outputJson:
                    outputJson.write(json.dumps(jsonData, indent=4))
                outputJson.close()
                
                with open("/localstorage2/temp/zsdt/static/output/jsons/"+json_to_find) as jsonDataFile:
                    jsonData_str = jsonDataFile.read()
                jsonDataFile.close()
                
                sqoop_cmd = "/usr/bin/python3.6 /localstorage2/temp/zsdt/ingestion_utility/sqoop_ingestion_util.py --globalParamFilePath /localstorage2/uat/data/common/raw-zone/edge/unix/param/ingestion_utility/global_param_uat.json --jobParamFilePath /localstorage2/temp/zsdt/static/output/jsons/"+json_to_find+" --env uat --alertEmail "+alert_email+" --logFilePath "+logFile
                
                with open("/localstorage2/temp/zsdt/static/output/pipelines/"+db2_schema.strip().lower()+"_"+db2_table.strip().lower()+"_" + str(run_count+1) + "_pipeline.sh", "w") as pipelineFile:
                    pipelineFile.write(sqoop_cmd+"\n\n"+post_processing_cmd)
                bash_cmd = "/usr/bin/bash /localstorage2/temp/zsdt/static/output/pipelines/"+db2_schema.strip().lower()+"_"+db2_table.strip().lower()+"_" + str(run_count+1) + "_pipeline.sh"
                
                bash_cmd_lst = bash_cmd.split()
                
                with open("/localstorage2/temp/zsdt/static/input/counts/"+db2_schema.strip().lower()+"_"+db2_table.strip().lower()+"_count.txt", "w") as countFile:
                    countFile.write(str(next_run_count_value))
                subprocess.Popen(bash_cmd_lst)
                
                return render_template('success.html', logFilePath = logFile, jsonData = jsonData_str)
            else:
                return render_template('failure.html', failure_msg = "Table not found in IDM Migration Scope List; If you think it's a mistake, please contact admin!")
        else:
            return render_template('failure.html', failure_msg = "Table not found in IDM Migration Scope List; If you think it's a mistake, please contact admin!")
    return render_template('incrLoadForm.html', form=form)

@app.route('/fullLoadForm', methods=['GET', 'POST'])
def fullLoadInput():
    form = LoginForm()
    if request.method == 'POST':
        db2_schema = request.form.get('db2_schema')
        db2_table = request.form.get('db2_table')
        bq_project = request.form.get('bq_project')
        bq_dataset = request.form.get('bq_dataset')
        bq_table = request.form.get('bq_table')
        delimeter = request.form.get('delimeter')
        split_by_column = request.form.get('split_by_column')
        no_of_mappers = request.form.get('no_of_mappers')
        post_processing_cmd = request.form['post_processing_cmd']
        alert_email = request.form.get('alert_email')
        
        target_table_name = bq_project + "." + bq_dataset + "." + bq_table
        
        json_to_find = db2_schema.strip().lower() + "_" + db2_table.strip().lower() + "_hist_copy_full_load.json"
        
        if db2_schema.strip().lower() + "." + db2_table.strip().lower() in db2_tables_list:
            if json_to_find in db2_jsons_list:
                
                with open("/localstorage2/temp/zsdt/static/input/counts/"+db2_schema.strip().lower()+"_"+db2_table.strip().lower()+"_count.txt") as countFile:
                    run_count = int(countFile.read())
                countFile.close()
                next_run_count_value = run_count + 1
                
                logFile = "/localstorage2/temp/zsdt/logs/" + db2_schema.strip().lower()+"_"+db2_table.strip().lower()+"_" + str(run_count+1) + "_full_load.log"
                
                with open("/localstorage2/temp/zsdt/static/input/jsons/"+json_to_find) as jsonFile:
                    jsonData = json.load(jsonFile)
                jsonData["TARGET_TABLE_NAME"] = target_table_name
                
                if delimeter.strip() != '':
                    jsonData["DELIMITER"] = delimeter
                if split_by_column.strip() != '':
                    jsonData["SPLIT_BY_COL"] = split_by_column
                if no_of_mappers.strip() != '':
                    jsonData["NUM_MAPPERS"] = no_of_mappers
                
                
                with open("/localstorage2/temp/zsdt/static/output/jsons/"+json_to_find, "w") as outputJson:
                    outputJson.write(json.dumps(jsonData, indent=4))
                outputJson.close()
                
                with open("/localstorage2/temp/zsdt/static/output/jsons/"+json_to_find) as jsonDataFile:
                    jsonData_str = jsonDataFile.read()
                jsonDataFile.close()
                
                sqoop_cmd = "/usr/bin/python3.6 /localstorage2/temp/zsdt/ingestion_utility/sqoop_ingestion_util.py --globalParamFilePath /localstorage2/uat/data/common/raw-zone/edge/unix/param/ingestion_utility/global_param_uat.json --jobParamFilePath /localstorage2/temp/zsdt/static/output/jsons/"+json_to_find+" --env uat --alertEmail "+alert_email+" --logFilePath "+logFile
                
                with open("/localstorage2/temp/zsdt/static/output/pipelines/"+db2_schema.strip().lower()+"_"+db2_table.strip().lower()+"_" + str(run_count+1) + "_pipeline.sh", "w") as pipelineFile:
                    pipelineFile.write(sqoop_cmd+"\n\n"+post_processing_cmd)
                bash_cmd = "/usr/bin/bash /localstorage2/temp/zsdt/static/output/pipelines/"+db2_schema.strip().lower()+"_"+db2_table.strip().lower()+"_" + str(run_count+1) + "_pipeline.sh"
                
                bash_cmd_lst = bash_cmd.split()
                
                with open("/localstorage2/temp/zsdt/static/input/counts/"+db2_schema.strip().lower()+"_"+db2_table.strip().lower()+"_count.txt", "w") as countFile:
                    countFile.write(str(next_run_count_value))
                subprocess.Popen(bash_cmd_lst)
                
                return render_template('success.html', logFilePath = logFile, jsonData = jsonData_str)
            else:
                return render_template('failure.html', failure_msg = "Table not found in IDM Migration Scope List; If you think it's a mistake, please contact admin!")
        else:
            return render_template('failure.html', failure_msg = "Table not found in IDM Migration Scope List; If you think it's a mistake, please contact admin!")
    return render_template('fullLoadForm.html', form=form)
    

    
netstat -tulnp | grep :1997

export FLASK_APP=main.py
flask run -h 0.0.0.0 -p 1997

nohup - 2538 | 12867 | 863 | 30659 | 4477 | 15640 | 4332 | 24166 | 29189 | 17932 | 13716 | 26968 | 19327 | 11055

1) Advanced Options
2) Generic JDBC connections
3) Hadoop
4) List of multiple tables to load
5) Logging
6) Progress Bar

2829 | 2760

"""