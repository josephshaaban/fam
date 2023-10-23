import json
import pandas as pd
from sqlalchemy import create_engine, types as sqlalchemy_types

from utils import (
  CustomDict,
  dict_fields_with_levels,
  dict_depth,
  sub_fields_depth,
)


fn = r'data.json'

with open(fn, encoding="UTF-8") as f:
  data = json.load(f)

data = CustomDict(data)

# Collects some info about Data
print("Depth of data obj:", data.depth)
print("Depth of properties obj:", dict_depth(data['properties']))

obj_fields, arr_fields = dict_fields_with_levels(data['properties'])
print(f"Objects fields: {obj_fields}")
print(f"Array fields: {arr_fields}")
sub_fields_depth(data, obj_fields, prefix='object')
sub_fields_depth(data, arr_fields, prefix='array')

# The length of all data is: 25
# data['properties'][index]["live_viewing"] all the values are None
# price are: nested objects
df = pd.DataFrame(data['properties'])
v = df.drop(arr_fields, axis=1)

# some of your records seem NOT to have `Tags` key, hence `KeyError: 'Tags'`
# let's fix it
# price_keys = set()
# price_key_types = list()
# for r in data['properties']:
#   price_keys.update(r['price'].keys())

# for val in data['properties'][1]['price'].values():
#   price_key_types.append(val)

# print(price_keys, price_key_types)
# for r in data['properties']:
#     for price_key in price_keys:
#         if price_key in r['price']:
#             print(r['price'][price_key])

price = pd.json_normalize(data['properties'], record_path='images')
# Normalize dropped fields to be converted to a new table
normalized_fields = {}
for field in arr_fields:
  normalized_fields[field] = pd.json_normalize(
    data['properties'],field, ['id'], meta_prefix='parent_')

# con = sqlite3.connect("db.sqlite")
PG_USER = "postgres"
PG_PASS = "admin"
PG_HOST = "localhost"
PG_PORT = "5432"
PG_DB_NAME = "fam"
PG_CLIENT_ENCODING = "utf8"
eng = create_engine(
    f"postgresql+psycopg2://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB_NAME}",
    use_native_hstore=False, #isolation_level="REPEATABLE READ"
)
v.to_sql(
  'properties', con=eng, if_exists='replace', index=True,
  dtype={field: sqlalchemy_types.JSON for field in obj_fields})

for normalized_field_name, normalized_field_val in normalized_fields.items():
  normalized_field_val.to_sql(
    normalized_field_name, con=eng, if_exists='replace', index=True)

print()
print("===========================================================")
print("All records has inserted in the corresponding tables. DONE!")
