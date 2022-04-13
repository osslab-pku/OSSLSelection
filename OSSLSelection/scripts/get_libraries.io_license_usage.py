from bs4 import BeautifulSoup
import requests
import pandas as pd

url = "https://libraries.io/licenses"
response = requests.get(url)
soup = BeautifulSoup(response.text,"html.parser")
container_div = soup.body.find_all(recursive=False)[1]
row_div = container_div.find_all(recursive=False)[3]
col8_div = row_div.find_all(recursive=False)[0]

licenses_count = []
for i in col8_div.div.find_all(recursive=False):
    licenses_count.append([i.h4.div.a.text,i.h4.div.small.text])

column_name = ['license','count']
df = pd.DataFrame(licenses_count,columns=column_name)
df.to_csv(r'E:\OSSSelection\OSSSelection\homepage\libraries.io_license_usage.csv',index=None,encoding='utf-8')