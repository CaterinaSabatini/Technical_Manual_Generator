import sqlite3
import os
import sys

"""
Combines model fields into the full device name.

@param prod: Product name
@param fam: Family name
@param subfam: Subfamily name
@param showsubfam: Flag indicating whether to show subfamily
@param model: Model name
@param submodel: Submodel name
@return: Formatted device name as a string
"""
def format_name(prod, fam, subfam, showsubfam, model, submodel):

    pieces = []
    if prod is not None:
        pieces.append(prod)
    if fam is not None:
        pieces.append(fam)
    if subfam is not None and showsubfam == 1:
        pieces.append(subfam)
    if model is not None:
        pieces.append(model)
    if submodel is not None:
        pieces.append(submodel)
    return ' '.join(map(str, pieces)).strip()


"""
Extracts, formats, sorts, and saves unique device names to a new SQLite database.

@param input_db_path: Path to the source database
@param output_db_path: Path to the destination database
"""
def create_new_sorted_device_database(input_db_path="devices_database/modelli.sqlite", 
                                     output_db_path="devices_database/device.sqlite"): 
    


    if not os.path.exists(input_db_path):
        print(f"Error: Input database not found at {input_db_path}", file=sys.stderr)
        return


    try:
        db_input = sqlite3.connect(input_db_path)
        cur_input = db_input.cursor()
    except sqlite3.Error as e:
        print(f"Error connecting to source database {input_db_path}: {e}", file=sys.stderr)
        return

    db_output = sqlite3.connect(output_db_path)
    cur_output = db_output.cursor()
    

    cur_output.execute("CREATE TABLE IF NOT EXISTS devices (ID INTEGER PRIMARY KEY, DEVICE TEXT NOT NULL UNIQUE);")
    cur_output.execute("DELETE FROM devices;")
    db_output.commit()

    print(f"Reading data from {input_db_path}...")


    sql_query = """
    SELECT 
        MODEL.prod, FAMILIES.fam, FAMILIES.subfam, FAMILIES.showsubfam, MODEL.model, MODEL.submodel 
    FROM 
        MODEL 
    JOIN 
        FAMILIES ON MODEL.idfam = FAMILIES.id
    ORDER BY 
        MODEL.prod ASC, FAMILIES.fam ASC, FAMILIES.subfam ASC, MODEL.model ASC, MODEL.submodel ASC; 
    """
    
    try:
        cur_input.execute(sql_query)
        results = cur_input.fetchall()
    except sqlite3.OperationalError as e:
        print(f"Error executing query: {e}", file=sys.stderr)

        db_input.close()
        db_output.close()
        return
    

    unique_formatted_names = set(format_name(*row) for row in results if format_name(*row))
    sorted_names_list = sorted(list(unique_formatted_names))
    
    print(f"Found {len(sorted_names_list)} unique names. Inserting them in alphabetical order...")

    try:

        cur_output.executemany("INSERT INTO devices (DEVICE) VALUES (?);", [(name,) for name in sorted_names_list])
    except sqlite3.IntegrityError as e:
        print(f"Integrity Error during insertion: {e}", file=sys.stderr)
    

    db_output.commit()
    db_input.close()
    db_output.close()
    
    print("Operation completed. Names saved in alphabetical order to devices_database/device.sqlite.")

if __name__ == "__main__":
    os.makedirs("devices_database", exist_ok=True)
    create_new_sorted_device_database()