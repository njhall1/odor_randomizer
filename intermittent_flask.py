# -*- coding: utf-8 -*-
"""
Created on Thu Apr  3 20:45:50 2025

@author: nathhall
"""


from flask import Flask, render_template, request
import pandas as pd
import random

app = Flask(__name__)

def randomize (mydict):
        
        mydict["target_frequency"]=float(mydict["target_frequency"])
        mydict["number_of_trials"]=int(mydict["number_of_trials"])
        mydict["probe"]=int(mydict["probe"])
        mydict['reinforce_targets']=float(mydict["reinforce_targets"])
        mydict["reinforce_blanks"]=float(mydict["reinforce_blanks"])
        
        #Balance everything in blocks of n trials (default is 10 trials)
        block_number=10
        nblocks=mydict["number_of_trials"]//block_number
        if mydict["number_of_trials"]%block_number!=0:
            nblocks+=1
            #In future add a check and warning that blocks don't match number of trials
            #Right now, just make more trials then necessary and last block wont be balanced
     
        probes=[]
        for i in range(0, mydict["probe"]):
            probes.append(1)
        for i in range(0, mydict["number_of_trials"]-mydict["probe"]):
            probes.append(0)
        random.shuffle(probes)
        
        
        targ_pres=[]
        reinforce=[]
        for i in range(0,nblocks):
            #Caluclate total number of target present rounded  down to nearest integer
            n_targets=(block_number*mydict["target_frequency"])//1
            n_targets=int(n_targets)
            n_blanks=block_number-n_targets
            
            #How many Targets & blanks to reinforce
            n_targets_reinforce=int(n_targets*mydict["reinforce_targets"]//1)
            n_blanks_reinforce=int(n_blanks*mydict["reinforce_blanks"]//1)
            
            #How many Targts & Blanks to NOT reinforce
            n_targets_not_reinforce=n_targets-n_targets_reinforce
            n_blanks_not_reinforce=n_blanks-n_blanks_reinforce
            
            #Create a list of whether to reinforce targets or not
            target_reinforce=[]
            for i in range(0, n_targets_reinforce):
                target_reinforce.append(1)
            for i in range(0, n_targets_not_reinforce):
                target_reinforce.append(0)
            random.shuffle(target_reinforce)
            
            #Create a list whether to reinforce blanks or not
            blank_reinforce=[]
            for i in range(0, n_blanks_reinforce):
                blank_reinforce.append(1)
            for i in range(0, n_blanks_not_reinforce):
                blank_reinforce.append(0)
            random.shuffle(blank_reinforce)
            
            #Create a list that adds the correct number of blanks and targets
            temp_targ_pres=[]
            for i in range(0,n_targets):
                temp_targ_pres.append(1)
                reinforce.append(target_reinforce[i])
            for i in range(0, n_blanks):
                temp_targ_pres.append("blank")
                reinforce.append(blank_reinforce[i])

            random.shuffle(temp_targ_pres)
            targ_pres=targ_pres+temp_targ_pres

        #Calulate and even number of targets at each olfactometer
        number_olf_per_block= n_targets//len(mydict["found_olfactometers"])
        number_olf_remainder= n_targets % len(mydict["found_olfactometers"])
      
        #Create a shuffled list of target olfactometers balanced by block
        target_olfactometer=[]
        for i in range(0,nblocks):
            temp_target_olfactometer=[]
            for a in mydict["found_olfactometers"]:
                for c in range(0, number_olf_per_block):
                    temp_target_olfactometer.append(a)
            random.shuffle(temp_target_olfactometer)
            target_olfactometer=target_olfactometer+temp_target_olfactometer
            additionals=random.sample(mydict['found_olfactometers'],number_olf_remainder)
            target_olfactometer=target_olfactometer+additionals
        
        #create full list specifying odor position or blank
        index=0
        target_olfactometer2=[]
        for i in targ_pres:
            if i =='blank':
                target_olfactometer2.append("blank")
            else: 
                target_olfactometer2.append(target_olfactometer[index])
                index+=1
              
        
        #Create a dictionary where olfactometer is the key, and is a list of the odors
        #For example {'11':[AA, AB, AA, AB], '20':[cc, DD]}
        target_odors=[]
        non_target_odors=[]
        
        #create a big list, that weights target odors
        for i in range(0, mydict["number_of_trials"]):
            for targ in mydict["Target"]: #For each target odor
                for a in range(0, mydict["{}_weight".format(targ)]):
                    target_odors.append(targ)
           
            if len(mydict["Mixed Target"])>0:
                splitter=":"
                target_odors.append(splitter.join(mydict["Mixed Target"]))
            
            if len (mydict["Distractor Mix with Target"])>0:
                for targ in mydict["Target Mix with Distractor"]:
                    for dist in mydict["Distractor Mix with Target"]:
                        dist2=random.sample(mydict["Distractor Mix with Target"], mydict["mixture_numbers"]-1)
                        splitter=":"
                        odors=[targ]
                        odors=odors+dist2
                        target_odors.append(splitter.join(odors))
              
            for p in mydict["Probe"]:
                target_odors.append(p)
            #IF randomized, can shuffle here                        
                
        for i in range(0, mydict["number_of_trials"]*len(mydict["found_olfactometers"])):
            for dist in mydict["Distractor"]: #For each target odor
                for a in range(0, mydict["{}_weight".format(dist)]):
                    non_target_odors.append(dist)
                    
            for mixwith in mydict["Distractor Mix with Target"]:
                dist=random.sample(mydict["Distractor Mix with Target"], mydict["mixture_numbers"])
                splitter=":"
                dist2=splitter.join(dist)
                non_target_odors.append(dist2)
                
        
        
       
        odorDict={}
        for i in mydict['found_olfactometers']:
            odorDict[i]=[]
            
        for a in range(0, mydict["number_of_trials"]):
            for olfactometer in mydict["found_olfactometers"]:
                correct_olfactometer=target_olfactometer2[a]
                if olfactometer==correct_olfactometer:
                  #THis is a target trial
                    if probes[a]==1:
                        trial_odor=mydict["Probe"][0]
                        reinforce[a]=0
                    else:
                        trial_odor=target_odors.pop(0)
                    odorDict[olfactometer].append(trial_odor)
                else: 
                    trial_odor=non_target_odors.pop(0)
                    odorDict[olfactometer].append(trial_odor)
        
        
  
        return(odorDict,  reinforce)
        

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = {
            'found_olfactometers': list(range(1, int(request.form['num_positions']) + 1)),
            'num_odors': request.form['num_odors'],
            'number_of_trials': request.form['num_trials'],
            'target_frequency': request.form['target_freq'],
            'probe': int(request.form['probe'] or 0),
            'reinforce_targets': request.form['reinforce_targets'],
            'reinforce_blanks': request.form['reinforce_blanks'],
            'Target': [],
            'Distractor': [],
            'Probe': [],
            "Mixed Target":[],
            "Distractor Mix with Target":[],
            "Target Mix with Distractor": []
            
        }

        for i in range(int(request.form['num_odors'])):
            name = request.form.get(f'odor_name_{i}')
            type_ = request.form.get(f'odor_type_{i}')
            weight = request.form.get(f'odor_weight_{i}', 0)
            if type_ in data:
                data[type_].append(name)
            data[f"{name}_weight"] = int(weight)

        randomized_data, reinforce = randomize(data)
        randomized_data['reinforce'] = reinforce
        df = pd.DataFrame(randomized_data)
        return render_template('index.html', table=df.to_html(index=False, classes='table table-bordered table-sm'), form_data=request.form)

    return render_template('index.html', table=None, form_data=None)

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
