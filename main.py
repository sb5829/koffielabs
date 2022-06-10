import sqlite3
from typing import Union
import logging

import os
from fastapi import FastAPI, Query
import requests
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from fastapi.responses import FileResponse, Response

app = FastAPI()

# check same thread disabled in order to run multiple sql executions
conn = sqlite3.connect('koffie.db', check_same_thread=False)
logging.getLogger().setLevel(logging.INFO)


def create_table():
    # create table to store vin and cached results
    conn.execute("""CREATE TABLE VIN_STORAGE
                (ID INTEGER PRIMARY KEY AUTOINCREMENT     NOT NULL,
                VIN           TEXT    NOT NULL,
                MAKE          TEXT    NOT NULL,
                MODEL         TEXT    NOT NULL,
                YEAR          TEXT    NOT NULL,
                BODY          TEXT    NOT NULL);""")

    print("Table created successfully")


def insert_to_table(vin, cache):
    cur = conn.cursor()
    cur.execute("INSERT INTO VIN_STORAGE (VIN,CACHE) \
      VALUES (VIN, CACHE);")

    conn.close()


def decode_vin(vin):
    # call the vPIC api in order to decode the given VIN
    url = f'https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/{vin}?format=json'
    try:
        r = requests.get(url)
        json_response = r.json()
        # return as json response
        return json_response
    except Exception as e:
        logging.error(f"Unable to get response from vPIC API with exception {e}")
        return None


def retrieve_data():
    # select all the entries in the database and return them
    sql = """SELECT * FROM VIN_STORAGE;"""
    cur = conn.cursor()
    cur.execute(sql)
    results = cur.fetchall()
    logging.info(f"The results from retrieving the data for cached VINs are: {results}")
    return results


def store_results(response):
    # check that there has been a valid response with results given from API
    if response and response.get('Results'):
        results = response['Results'][0]
        vin = results.get('VIN')
        make = results.get('Make')
        model = results.get('Model')
        model_year = results.get('ModelYear')
        body_class = results.get('BodyClass')
        sql = """ INSERT INTO VIN_STORAGE (VIN, MAKE, MODEL, YEAR, BODY) VALUES(?, ?, ?, ?, ?);"""
        cur = conn.cursor()
        cur.execute(sql, (vin, make, model, model_year, body_class))
        logging.info(f"Entry for VIN {vin} was entered")
        return [make, model, model_year, body_class, vin]
    else:
        logging.error(f"Response was not available. Response message is: {response.get('message')}")
        return None


def vin_exists(vin):
    cur = conn.cursor()
    sql = """SELECT * FROM VIN_STORAGE WHERE VIN=?"""
    cur.execute(sql, (vin,))
    # the entry already exists, return result
    res = cur.fetchone()
    if res:
        print("Found!")
        logging.info(f"Entry for VIN {vin} was found in cache, return cached results")
        # return False as the vin entry was not cached
        return False, res
    # the entry does not exist, add it to the database
    else:
        logging.info(f"Entry for VIN {vin} was not found in cache, decoding VIN now")
        result = decode_vin(vin)
        res = store_results(result)
        # return True as VIN has been cached
        return True, res


def remove_vin(vin):
    cur = conn.cursor()
    # search if VIN is already cached in database
    vin_exist, res = vin_exists(vin)
    if not vin_exist:
        sql = """DELETE FROM VIN_STORAGE WHERE VIN=?"""
        logging.info(f"VIN {vin} has been deleted from the database")
        cur.execute(sql, (vin,))
        return True
    else:
        logging.error(f"VIN {vin} does not exist within the database records. Please provide a valid VIN to remove.")
        return False


def export_file():
    # get cached data
    result = retrieve_data()
    data = {}
    # create a column number for each of the entries
    for res in result:
        data['col'+str(res[0])] = [res[1], res[2], res[3], res[4], res[5]]
    # index will always be length of 5 because of the parameters already defined as make, model, year and body class
    # create data frame with data and number of items in each colum
    df = pd.DataFrame(data=data, index=[0, 1, 2, 3, 4])
    # convert dataframe into a table
    table = pa.Table.from_pandas(df)
    # use the table to write into parquet format
    file = pq.write_table(table, 'export_vin_cache.parquet')
    return file


@app.get("/lookup/")
# vin definition makes it required and makes sure that it is of length 17
def lookup(vin: str = Query(min_length=17, max_length=17)):
    # check if vin already exists within the database. If no records are found, vin exists will create entry, if found
    # vin_exists will query the results and return them
    exists, res = vin_exists(vin)
    try:
        if not exists:
            return {"vin": vin, "make": res[2], "model": res[3], "model_year": res[4],
                    "body_class": res[5], "cached": exists}
        else:
            return {"vin": vin, "make": res[0], "model": res[1], "model_year": res[2],
                    "body_class": res[3], "cached": exists}
    except Exception as e:
        return f"The request was unable to process due to exception: {e}"


@app.get("/remove/")
def read_item(vin: str= Query(min_length=17, max_length=17)):
    res = remove_vin(vin)
    return {"vin": vin, "cache_delete_success": res}


@app.get("/export/")
def read_item():
    export_file()
    root_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(root_dir, 'export_vin_cache.parquet')
    return FileResponse(file_path)


@app.get("/create_table")
def create_initial_table():
    create_table()
    return "Table created"
