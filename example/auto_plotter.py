#!/bin/env python
import os
import shutil
import subprocess


def main():
    
    base=os.getcwd()
    
        
    plottinglist=["dmw_neu_AV", "dmw_neu_PS", "dmw_neu_S", 
                    "ps50_neu_AV", "ps50_neu_PS", "ps50_neu_S",
                    "ps90_neu_AV", "ps90_neu_PS", "ps90_neu_S",
                    "static_neu_AV", "static_neu_PS", "static_neu_S",
                    "wprime_neu_AV", "wprime_neu_PS", "wprime_neu_S"]

    #~ plottinglist=["test"] 

    for plot in plottinglist:
        
        os.chdir(base+"/"+plot)
            
        if os.path.isfile(base+"/"+plot+"/plotting.py"):
            print "plotting.py already exists"  
        else:
            dir_src = base+"/python"
            dir_dst = base+"/"+plot+"/python"
            try:
                os.stat(dir_dst)
            except:
                os.mkdir(dir_dst)   
            for file in os.listdir(dir_src):
                print file 
                src_file = os.path.join(dir_src, file)
                dst_file = os.path.join(dir_dst, file)
                shutil.copy2(src_file, dst_file)
            shutil.copy2(base+"/Hypothesis.py", base+"/"+plot+'/Hypothesis.py')
            shutil.copy2(base+"/plotting.py", base+"/"+plot+'/plotting.py')
        try:
            subprocess.call(['./plotting.py', "--xmin",  "0", "--xmax", "6000"])
        except:
            print "there was an error with plotting.py"
            if os.path.isfile("plotting.py"):
                print "but it exists"
            else:
                print "and it doesnt exist"



if __name__=="__main__":
    main()
