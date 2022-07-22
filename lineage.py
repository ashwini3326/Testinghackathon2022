import pandas as pd
import json
import os
import shutil
#from google.cloud import bigquery

    
def download_dag_parsed_output(table_name):
    
    if table_name.count(".") != 2:
        return -1, "Table name not according to standards, please check!!"
    try:
        client = bigquery.Client()
        query = f"select distinct controlm_job_name, dag_id,task_id, source, target from {table_name} where trim(source) != '' and trim(target) != '' and source is not null and target is not null"
        #print("Executing Query : " + str(query))
        dataframe = (
            client.query(query)
                .result()
                .to_dataframe()
        )
        dataframe.to_csv(os.path.join('static', 'input', 'dag_parsed_output.csv'))
        
        try:
            if os.path.isdir(os.path.join('static', 'cached_lineage')):
                shutil.rmtree(os.path.join('static', 'cached_lineage'))
        except Exception as e:
            return -1, f"Lineage Data Source Refreshed from Source Table : {table_name} !! But failed to delete cache folder : {str(e)} !!"
        return 0, f"Lineage Data Source Refreshed from Source Table : {table_name} !! Also deleted cache folder !!"
    except Exception as e:
        return -1, str(e)
    
def newLineageBkp(cnt, target, lineageLevel, parentNode="null"):
    
    targetVisited.append(target)
    jsonData = {}
    
    count = cnt + 1
    
    if count > lineageLevel:
        return
    
    jsonData["name"] = target
    jsonData["parent"] = parentNode
    jsonData["children"] = []
    
    
    for n in range(len(csvFile)):
        
        innerTarget = csvFile.iloc[n]['target']
        sourceTableStr = csvFile.iloc[n]['source']
        
        if innerTarget == target:
            sourceTables = sourceTableStr.split(" | ")
            for pp in range(len(sourceTables)):
                if sourceTables[pp] not in targetVisited:
                    recursion_output = newLineage(count,sourceTables[pp], lineageLevel, target)
                    if recursion_output is not None:
                        jsonData["children"].append(recursion_output)
    return jsonData
    
def newLineage(cnt, ctm_name, dag_name, target, lineageLevel, parentNode="null"):
    
    targetVisited.append(target)
    jsonData = {}
    
    count = cnt + 1
    
    if count > lineageLevel:
        return
    
    jsonData["name"] = target
    jsonData["parent"] = parentNode
    jsonData["children"] = []
    
    
    for n in range(len(csvFile)):
        
        innerCtm = csvFile.iloc[n]['controlm_job_name']
        innerDag = csvFile.iloc[n]['dag_id']
        innerTarget = csvFile.iloc[n]['target']
        sourceTableStr = csvFile.iloc[n]['source']
        
        if innerTarget == target:
            if count == 1:
                if innerCtm == ctm_name and innerDag == dag_name:
                    sourceTables = sourceTableStr.split(" | ")
                    for pp in range(len(sourceTables)):
                        if sourceTables[pp] not in targetVisited:
                            recursion_output = newLineage(count, ctm_name, dag_name, sourceTables[pp], lineageLevel, target)
                            if recursion_output is not None:
                                jsonData["children"].append(recursion_output)
            else:
                sourceTables = sourceTableStr.split(" | ")
                for pp in range(len(sourceTables)):
                    if sourceTables[pp] not in targetVisited:
                        recursion_output = newLineage(count, ctm_name, dag_name, sourceTables[pp], lineageLevel, target)
                        if recursion_output is not None:
                            jsonData["children"].append(recursion_output)
    return jsonData

def generateLineage(ctm_name, dag_name, table_name, lineageLevel):
    
    if not os.path.isdir(os.path.join('static', 'cached_lineage')):
        os.makedirs(os.path.join('static', 'cached_lineage'))
    
    global csvFile
    csvFile = pd.read_csv(os.path.join('static', 'input', 'dag_parsed_output.csv'))
    global targetVisited
    targetVisited = []
    
    if table_name not in list(csvFile['target']):
        return "NO_LINEAGE_GENERATED", []
    
    if lineageLevel == "Max":
        lineageLevel = 15
    
    if os.path.exists(os.path.join("static", "cached_lineage", f"{table_name}_{ctm_name}_{dag_name}_{lineageLevel}.json")):
        return "CACHE_GENERATED", json.load(open(os.path.join("static", "cached_lineage", f"{table_name}_{ctm_name}_{dag_name}_{lineageLevel}.json")))
    targetNode = newLineage(0, ctm_name, dag_name, table_name, int(lineageLevel) + 1)

    with open(os.path.join("static", "cached_lineage", f"{table_name}_{ctm_name}_{dag_name}_{lineageLevel}.json"), "w") as f:
        f.write(json.dumps([targetNode], indent=4))
        
    return "NEW_GENERATED", [targetNode]
    
def newAllLineage(cnt, dag_name, target, lineageLevel, parentNode="null"):
    
    targetVisited.append(target)
    jsonData = {}
    
    count = cnt + 1

    if count > lineageLevel:
        return
    
    if count == 1:
        jsonData["name"] = "DAG: " + dag_name
        jsonData["parent"] = target
        jsonData["children"] = []
    else:
        jsonData["name"] = target
        jsonData["parent"] = parentNode
        jsonData["children"] = []
    
    for n in range(len(csvFile)):
        
        innerCtm = csvFile.iloc[n]['controlm_job_name']
        innerDag = csvFile.iloc[n]['dag_id']
        innerTarget = csvFile.iloc[n]['target']
        sourceTableStr = csvFile.iloc[n]['source']
        
        if innerTarget == target:
            if count == 1:
                if innerDag == dag_name:
                    sourceTables = sourceTableStr.split(" | ")
                    for pp in range(len(sourceTables)):
                        if sourceTables[pp] not in targetVisited:
                            recursion_output = newAllLineage(count, dag_name, sourceTables[pp], lineageLevel, target)
                            if recursion_output is not None:
                                jsonData["children"].append(recursion_output)
            else:
                sourceTables = sourceTableStr.split(" | ")
                for pp in range(len(sourceTables)):
                    if sourceTables[pp] not in targetVisited:
                        recursion_output = newAllLineage(count, dag_name, sourceTables[pp], lineageLevel, target)
                        if recursion_output is not None:
                            jsonData["children"].append(recursion_output)
    return jsonData
    
def generateAllLineage(dags_list, table_name, lineageLevel):
    
    if not os.path.isdir(os.path.join('static', 'cached_lineage')):
        os.makedirs(os.path.join('static', 'cached_lineage'))
    
    global csvFile
    csvFile = pd.read_csv(os.path.join('static', 'input', 'dag_parsed_output.csv'))
    global targetVisited
    targetVisited = []
    
    if table_name not in list(csvFile['target']):
        return "NO_LINEAGE_GENERATED", []
    
    if lineageLevel == "Max":
        lineageLevel = "15"
    
    if os.path.exists(os.path.join("static", "cached_lineage", f"{table_name}_all_dags_{lineageLevel}.json")):
        return "CACHE_GENERATED", json.load(open(os.path.join("static", "cached_lineage", f"{table_name}_all_dags_{lineageLevel}.json")))
    
    dagsNode = []
    for dags_list_name in dags_list:
        dagsNode.append(newAllLineage(0, dags_list_name, table_name, int(lineageLevel) + 1))
    
    targetNode = {}
    targetNode["name"] = table_name
    targetNode["parent"] = "null"
    targetNode["children"] = dagsNode
    
    with open(os.path.join("static", "cached_lineage", f"{table_name}_all_dags_{lineageLevel}.json"), "w") as f:
        f.write(json.dumps([targetNode], indent=4))
        
    return "NEW_GENERATED", [targetNode]
