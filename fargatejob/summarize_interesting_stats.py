import os
import boto3
import pandas as pd
from io import StringIO


# Read all CSV's
print(f'Reading files from bucket cruncheddata/')
s3_resource = boto3.resource('s3')
S3_BUCKET = os.environ['S3_BUCKET']
bucket = s3_resource.Bucket(S3_BUCKET)
crunched_s3_objects = list(bucket.objects.filter(
    Prefix='cruncheddata/'
))
crunched_keys = [ o.key for o in crunched_s3_objects ]

print('Files Found:', crunched_keys)

# Concat all dataframes together
cruncheddata_dfs = []
for key in crunched_keys:
    obj = bucket.Object(key=key)
    df = pd.read_csv(obj.get()['Body'], sep=",", encoding = "utf-8")
    cruncheddata_dfs.append(df)

summary_df = pd.concat(cruncheddata_dfs)
summary_df['Estimated_Revenue'] = summary_df.Total_Units_Sold * summary_df.Average_Price_Of_Unit
summary_df.sort_values('Total_Units_Sold', axis=0, ascending=False, inplace=True)

pd.set_option('display.max_columns', None)

# Get top 5 sold by units
top_by_units_sold_df = summary_df.head(5)
print('Top Items Sold By Total Units Sold')
print(top_by_units_sold_df)
print(f'Writing data to bucket at Key=summarizeddata/top_items_by_units.csv')
csv_buffer = StringIO()
top_by_units_sold_df.to_csv(csv_buffer, sep=',', encoding = "utf-8", index=False)
bucket.put_object(
    Key=f'summarizeddata/top_items_by_units.csv.csv',
    Body=csv_buffer.getvalue()
)

# Get top 5 sold by Estimated Revenue
summary_df.sort_values('Estimated_Revenue', axis=0, ascending=False, inplace=True)
top_by_revenue_df = summary_df.head(5)
print('Top Items Sold By Estimated Revenue')
print(top_by_revenue_df)
print(f'Writing data to bucket at Key=summarizeddata/top_items_by_revenue.csv')
csv_buffer = StringIO()
top_by_revenue_df.to_csv(csv_buffer, sep=',', encoding = "utf-8", index=False)
bucket.put_object(
    Key=f'summarizeddata/top_items_by_revenue.csv',
    Body=csv_buffer.getvalue()
)
