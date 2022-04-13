import pandas as pd

df = pd.read_csv('E:\\oss_license_selection_analyze\\src\\licenses_terms_58.csv')

dd = df[df['license']=='Apache-2.0'].to_dict(orient='records')
print(dd)