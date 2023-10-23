import pymongo
import sys
import json


# Authenticate to remote MongoDB server
try:
  client = pymongo.MongoClient(
    "mongodb+srv://josephsha3ban:NbUVQq9QxNXYe02Q@cluster0.7qwnixv.mongodb.net/")
  
# return a friendly error if a URI error is thrown 
except pymongo.errors.ConfigurationError:
  print(
    "An Invalid URI host error was received. Is your"
    " Atlas host name correct in your connection string?"
    )
  sys.exit(1)

# use a database named "myDatabase"
db = client.myDatabase

# use a collection named "flats"
my_collection = db["flats"]

# Load Fam Properties data from json file
with open('data.json', 'r', encoding='utf8') as f:
    flat_documents = json.load(f)

# drop the collection in case it already exists
try:
  my_collection.drop()  

# return a friendly error if an authentication error is thrown
except pymongo.errors.OperationFailure:
  print(
    "An authentication error was received. Are your username"
     " and password correct in your connection string?"
    )
  sys.exit(1)

# INSERT DOCUMENTS
#
# You can insert individual documents using collection.insert_one().
# In this example, we're going to create four documents and then 
# insert them all with insert_many().
try: 
 result = my_collection.insert_many(flat_documents)

# return a friendly error if the operation fails
except pymongo.errors.OperationFailure:
  print(
    "An authentication error was received. Are you sure your"
    "database user is authorized to perform write operations?"
    )
  sys.exit(1)
else:
  inserted_count = len(result.inserted_ids)
  print("I inserted %x documents." %(inserted_count))

  print("\n")
