import pandas as pd 
import textstat
import os

# 分值越高，越难理解
content = []
rootdir = r'E:\OSSLSelection\OSSLSelection\homepage\static\doc\license\text'
for root,_,filenames in os.walk(rootdir):
    for filename in filenames:
        if filename.find('.txt') == -1:
            continue
        print(root)
        print(filename)
        fullfilename = rootdir +'\\'+ filename
        with open(fullfilename,'r',encoding='utf-8') as f:
            lines = f.read()
            FOG = textstat.gunning_fog(lines.lower())
            ARI=textstat.automated_readability_index(lines.lower())
            CLI=textstat.coleman_liau_index(lines.lower())
            mean=(FOG+ARI+CLI)/3
            content.append([filename,FOG,ARI,CLI,mean])
dd=pd.DataFrame(content,columns=['ID','FOG','ARI','CLI','mean'])
dd.to_csv(r"E:\oss_license_selection_analyze\license_readability.csv")
