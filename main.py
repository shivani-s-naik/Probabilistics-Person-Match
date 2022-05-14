from flask import Flask, request, jsonify,render_template
import pandas as pd
import numpy as np

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta

app=Flask(__name__)

def fuzzyoperation(input_data):
    df=pd.read_excel('Person Dataset.xlsx')
    df["FullName"]=df['FirstName']+" "+df.LastName
    df["Age"]=df.DOB.apply(lambda x:(relativedelta(today,x)).years)

    input_data["FullName"]=input_data['FirstName']+" "+input_data["LastName"]
    input_data.DOB=pd.to_datetime(input_data.DOB)
    input_data["Age"]=input_data["Age"]=input_data.DOB.apply(lambda x:(relativedelta(today,x)).years)
    temp_df=df.copy()
    temp_df

    temp_df["name_per"]=temp_df["FullName"].apply(lambda x:fuzz.partial_ratio(x,input_data["FullName"][0]))
    temp_df["occupation_per"]=df["Occupation"].apply(lambda x:fuzz.token_set_ratio(x,input_data["Occupation"][0]))
    temp_df["gender_per"]=df["Gender"].apply(lambda x:fuzz.ratio(x.lower(),input_data["Gender"][0].lower()))
    temp_df["city_per"]=df["City"].apply(lambda x:fuzz.partial_ratio(x,input_data["City"][0]))
    temp_df["caste_per"]=df["Caste/Religion"].apply(lambda x:fuzz.partial_ratio(x,input_data["Caste/Religion"][0]))
    temp_df["pincode_per"]=df["PinCode"].apply(lambda x:fuzz.ratio(str(x),str(input_data["PinCode"][0])))
    temp_df["age_per"]=df["Age"].apply(lambda x:fuzz.ratio(str(x),str(input_data["Age"][0])))

    temp_df["mean_per"]=temp_df[["name_per","caste_per","pincode_per","occupation_per","gender_per","city_per","age_per"]].mean(axis=1)

    return temp_df.sort_values(by="mean_per",ascending=False).head(5)

weights_dict={
    "FirstName_wt" : 0.1,
    "LastName_wt" : 0.2,
    "DOB_wt" : 0.25,
    "Caste/Religion_wt" : 0.05,
    "Occupation_wt" : 0.05,
    "Gender_wt" : 0.25,
    "City_wt" : 0.05,
    "PinCode_wt" : 0.05
}
data={}
def GetFuzzyWtAvg(df,weights,input_dict):
    avg_score=0
    try:
        fscore=[]
        fscore.append(fuzz.partial_token_set_ratio(df["FirstName"],input_dict["FirstName"])*weights["FirstName_wt"])
        fscore.append(fuzz.partial_token_set_ratio(df["LastName"],input_dict["LastName"])*weights["LastName_wt"])
        fscore.append(fuzz.ratio(df["DOB"],input_dict["DOB"])*weights["DOB_wt"])
        fscore.append(fuzz.partial_ratio(df["Caste/Religion"],input_dict["Caste/Religion"])*weights["Caste/Religion_wt"])
        fscore.append(fuzz.partial_token_set_ratio(df["Occupation"],input_dict["Occupation"])*weights["Occupation_wt"])
        fscore.append(fuzz.ratio(df["Gender"],input_dict["Gender"])*weights["Gender_wt"])
        fscore.append(fuzz.partial_ratio(df["City"],input_dict["City"])*weights["City_wt"])
        fscore.append(fuzz.partial_token_set_ratio(df["PinCode"],input_dict["PinCode"])*weights["PinCode_wt"])
        avg_score=sum(fscore)/sum(weights.values())

    except:
        avg_score=0
    return avg_score

def generateresult():
    #if form.is_submitted():
        data={}
        data["FirstName"]=request.form["Fname"]
        data["LastName"]=request.form["Lname"]
        data["DOB"]=request.form["dob"]
        data["Gender"]=request.form["gender"]
        data["Occupation"]=request.form["occupation"]
        data["Caste/Religion"]=request.form["caste/religion"]
        data["City"]=request.form["city"]
        data["PinCode"]=request.form["pincode"]
        df=pd.read_excel('Person Dataset.xlsx')
        df.DOB=df.DOB.astype(str)
        df["Score"]=df.apply(GetFuzzyWtAvg,weights=weights_dict,input_dict=input_dict,axis=1)
        final_df=df.sort_values(by="Score",ascending=False,axis=0).iloc[0:10,:].hide_index()
        return render_template('output.html',tables=[final_df.to_html(classes='data', header="true",index="false")],titles=final_df.columns.values) 


@app.route('/FetchForm',methods=['GET','POST'])
def FetchForm():
    return render_template('home.html')

@app.route('/Result',methods=['POST'])
def generateresult():
    #if form.is_submitted():
    
    data["FirstName"]=request.form["Fname"]
    data["LastName"]=request.form["Lname"]
    data["DOB"]=request.form["dob"]
    data["Gender"]=request.form["gender"]
    data["Occupation"]=request.form["occupation"]
    data["Caste/Religion"]=request.form["caste/religion"]    
    data["City"]=request.form["city"]
    data["PinCode"]=request.form["pincode"]
    df=pd.read_excel('Person Dataset.xlsx')
    df.DOB=df.DOB.astype(str)
    df["Score"]=df.apply(GetFuzzyWtAvg,weights=weights_dict,input_dict=data,axis=1)
    data_df=pd.DataFrame(data,index=[0])
    final_df=df.sort_values(by="Score",ascending=False,axis=0).iloc[0:10,:].drop('Address',axis=1)
    
    return render_template('output.html',tables=[final_df.to_html(classes='data', header=True,index=False),data_df.to_html(header=True)],
    titles=['na','Result','Input']) 


@app.route('/FindSimilarity', methods = ['POST'])
def FindSimilarity():
    data=request.get_json()
    input_dict=dict(data)    
    df=pd.read_excel('Person Dataset.xlsx')
    df.DOB=df.DOB.astype(str)
    df["Score"]=df.apply(GetFuzzyWtAvg,weights=weights_dict,input_dict=input_dict,axis=1)
    # key=data.keys()
    # df=pd.DataFrame(data=data.values(),columns="FirstName LastName DOB Caste/Religion PinCode Occupation Gender City".split(' '),index=[0])
    final_df=df.sort_values(by="Score",ascending=False,axis=0).iloc[0:10,:]
    final_dict={}
    final_dict['FNm']=final_df.FirstName[0]
    final_dict['LNm']=final_df.LastName[0]
    final_dict['dob']=final_df.DOB[0]
    final_dict['gender']=final_df.Gender[0]
    final_dict['city']=final_df.City[0]
    final_dict['Caste/Religion']=final_df['Caste/Religion'][0]
    final_dict['PinCode']=final_df.PinCode[0]
    final_dict['Occupation']=final_df.Occupation[0]
    
    final_dict['Score']=final_df.Score[0]
    titles=df.columns
    return render_template('output.html',tables=[final_df.to_html(classes='data', header="true")],titles=final_df.columns) 


if __name__=='__main__':
    app.run(debug=True) 