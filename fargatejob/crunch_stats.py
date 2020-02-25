import argparse
import os
import boto3
import pandas as pd
from io import StringIO

# Parse Command Line Arguments
parser = argparse.ArgumentParser(description='Add some integers.')
parser.add_argument('startitem', metavar='s', type=int,
                    help='What item of the OnlineRetail.csv should I start at')
parser.add_argument('enditem', metavar='e', type=int,
                    help='What item of the OnlineRetail.csv should I end at')
args = parser.parse_args()

START_ITEM = args.startitem;
END_ITEM = args.enditem;
print(f'Crunching stats for items #{START_ITEM} to #{END_ITEM} of OnlineRetail.csv')

# Read CSV into a Dataframe
print(f'Reading data from Key=rawdata/OnlineRetail.csv')
s3_resource = boto3.resource('s3')
S3_BUCKET = os.environ['S3_BUCKET']
bucket = s3_resource.Bucket(S3_BUCKET)
obj = bucket.Object(key=f"rawdata/OnlineRetail.csv")
df = pd.read_csv(obj.get()['Body'], sep=",", encoding = "utf-8")
items = df.Description.unique()

# Crunching Stats
stats_list = []
for i, i_description in enumerate(items[START_ITEM : END_ITEM]):
    print(f'Crunching Stats for item: {i_description}')
    item_df = df[df.Description == i_description]
    stat = (
        i + START_ITEM,
        i_description,
        item_df.Quantity.sum(),
        item_df.UnitPrice.mean()
    )
    print(stat)
    stats_list.append(stat)
    del(item_df)
stats_df = pd.DataFrame(stats_list, columns =['Item_Number', 'Item', 'Total_Units_Sold', 'Average_Price_Of_Unit'])

# Publishing Stats
print(f'Writing data to bucket at Key=cruncheddata/{START_ITEM}_{END_ITEM}.csv')
csv_buffer = StringIO()
stats_df.to_csv(csv_buffer, sep=',', encoding = "utf-8", index=False)
bucket.put_object(
    Key=f'cruncheddata/{START_ITEM}_{END_ITEM}.csv',
    Body=csv_buffer.getvalue()
)
