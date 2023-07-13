import sqlite3
import requests
import json
import os
from google.cloud import language_v1
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "C:/Users/nmarr/OneDrive/Documents/Benchcube/Code/benchcube-testing-bf0841e1db42.json"
"--------------------------------------------------------------------------------------------"
conn = sqlite3.connect('C:/Users/nmarr/OneDrive/Documents/Benchcube/Data/ConstructMapping.db')
cursor = conn.cursor()

cursor.execute("SELECT Response FROM Response LIMIT 1")
rows = cursor.fetchall()
print(rows)

cursor.execute("PRAGMA table_info(Response)")
columns = cursor.fetchall()
column_names = [column[1] for column in columns]

if 'Category' not in column_names:
    cursor.execute('ALTER TABLE Response ADD COLUMN Category TEXT')
    conn.commit()

"--------------------------------------------------------------------------------------------"
def classify_text(responses):
    client = language_v1.LanguageServiceClient()
    for response in responses:
        text = str(response)
        text = text[1:-2]
        print(text)
        type_ = language_v1.Document.Type.PLAIN_TEXT
        language = "en"
        document = {"content":text, "type_": type_, "language": language}

        content_categories_version = (language_v1.ClassificationModelOptions.V2Model.ContentCategoriesVersion.V2)
        classify = client.classify_text(
            request = {
                "document" : document,
                "classification_model_options": {
                    "v2_model": {"content_categories_version": content_categories_version}
                }
            }
        )
        delimeter = ', '
        for category in classify.categories:
            print(f"Category Name: {category.name}")
            print(f"Category Name: {category.confidence}")

    joined_categories = delimeter.join(str(category.name) for category in classify.categories)
    print(joined_categories)
    cursor.execute("UPDATE Response SET Category=? WHERE Response = ?", (joined_categories,text))


conn.commit()
classify_text(rows)
cursor.close()
conn.close()


