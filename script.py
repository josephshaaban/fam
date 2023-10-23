import json
import pandas as pd
from sqlalchemy import create_engine, types as sqlalchemy_types

from utils import (
  CustomDict,
  dict_fields_with_levels,
  dict_depth,
  sub_fields_depth,
)


# Reading the data json file
fn = r'data.json'
with open(fn, encoding="UTF-8") as f:
  data = json.load(f)

# Use our helper class to cast loaded json into custom dict
data = CustomDict(data)

# Collects some info about Data
print("Depth of data obj:", data.depth)
print("Depth of properties obj:", dict_depth(data['properties']))

# Extracts the fields that need to be normalized and casted
obj_fields, arr_fields = dict_fields_with_levels(data['properties'])
print(f"Objects fields: {obj_fields}")
print(f"Array fields: {arr_fields}")

# Be sure our data has no deeper fields
sub_fields_depth(data, obj_fields, prefix='object')
sub_fields_depth(data, arr_fields, prefix='array')

# read data as pandas data frame
df = pd.DataFrame(data['properties'])
properties = df.drop(arr_fields, axis=1)

# Normalize dropped fields to be converted to a new table
normalized_fields = {}
for field in arr_fields:
  normalized_fields[field] = pd.json_normalize(
    data['properties'],field, ['id'], meta_prefix='parent_')

# Postgres configs
PG_USER = "postgres"
PG_PASS = "admin"
PG_HOST = "localhost"
PG_PORT = "5432"
PG_DB_NAME = "fam"
PG_CLIENT_ENCODING = "utf8"

# create Postgres connection via Alchemy
eng = create_engine(
    f"postgresql+psycopg2://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB_NAME}",
    use_native_hstore=False,
    # isolation_level="Autocommit",
)

# Create the main table `properties`
properties.to_sql(
  'properties', con=eng, if_exists='replace', index=True,
  # cast dict fields to Json fields in the table
  dtype={field: sqlalchemy_types.JSON for field in obj_fields})

# Create new tables in database for each normalized field
for normalized_field_name, normalized_field_val in normalized_fields.items():
  normalized_field_val.to_sql(
    normalized_field_name, con=eng, if_exists='replace', index=True)

print()
print("===========================================================")
print("All records has inserted in the corresponding tables. DONE!")
print()
