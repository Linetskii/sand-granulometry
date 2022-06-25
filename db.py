import sqlite3
from os import path, getcwd
from datetime import date


def create_connection(pth):
    """
    Create the connection with SQL database
    :param pth: name of database file
    :return: connection with database
    """
    con = None
    try:
        con = sqlite3.connect(path.join(getcwd(), pth))
        print('Connection to sqlite DB successful')
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred")
    return con


def execute_query(query: str):
    """
    Execute query
    :param query: SQL query
    """
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print('Query executed successfully')
    except sqlite3.Error as e:
        print(f"Can`t execute the query. The error '{e}' occurred")


def read_query(query):
    """
    Execute SELECT query, returns selected
    :param query: SQL query
    :return: result of SELECT query
    """
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except sqlite3.Error as e:
        print(f"Can`t read the query. The error '{e}' occurred")


def create_db():
    """
    create locations, zones, persons, samples and fractions tables
    :return:
    """
    # location table query
    create_locations_table = '''
    CREATE TABLE IF NOT EXISTS locations (
    location_id INTEGER PRIMARY KEY,
    location TEXT,
    UNIQUE(location) ON CONFLICT IGNORE
    );
    '''
    # zone table query
    create_zones_table = '''
    CREATE TABLE IF NOT EXISTS zones (
    zone_id INTEGER PRIMARY KEY,
    zone TEXT,
    UNIQUE(zone) ON CONFLICT IGNORE
    );
    '''
    # persons table query
    create_persons_table = '''
    CREATE TABLE IF NOT EXISTS persons (
    person_id INTEGER PRIMARY KEY,
    person TEXT,
    UNIQUE(person) ON CONFLICT IGNORE
    );
    '''
    # samples table query
    create_samples_table = '''
    CREATE TABLE IF NOT EXISTS samples(
    sample_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sample TEXT,
    location_id INTEGER NOT NULL,
    zone_id INTEGER NOT NULL,
    latitude TEXT,
    longitude TEXT,
    sampling_date TEXT,
    collector INTEGER NOT NULL,
    analysis_date TEXT,
    performer INTEGER NOT NULL,
    Mdφ REAL,
    Mz REAL,
    QDφ REAL,
    σ_1 REAL,
    Skqφ REAL,
    Sk_1 REAL,
    KG REAL,
    SD REAL,
    FOREIGN KEY (location_id) REFERENCES locations (location_id) ON DELETE CASCADE,
    FOREIGN KEY (zone_id) REFERENCES zones (zone_id) ON DELETE CASCADE,
    FOREIGN KEY (collector) REFERENCES persons (person_id) ON DELETE CASCADE,
    FOREIGN KEY (performer) REFERENCES persons (person_id) ON DELETE CASCADE
    );
    '''
    # fractions table query
    create_fractions_table = '''
    CREATE TABLE IF NOT EXISTS fractions (
    fraction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sample_id INTEGER NOT NULL,
    fraction INTEGER,
    weight REAL,
    FOREIGN KEY (sample_id) REFERENCES sample (sample_id)
    ON DELETE CASCADE
    );
    '''
    execute_query(create_locations_table)
    execute_query(create_zones_table)
    execute_query(create_persons_table)
    execute_query(create_fractions_table)
    execute_query(create_samples_table)


def get_id(item: str, val: str) -> str:
    """
    Get desired id from SQL database. Val must be in column "item" of table "item"+"s" with id in "item"+"_id" column.

    :param item: column name with desired value
    :param val: value to search
    :return: item_id of value in items table
    """
    query = f'''
    SELECT {item}_id
    FROM {item}s
    WHERE {item} = "{val}"
    '''
    return read_query(query)[0][0]


def update(column: str, table: str = None) -> None:
    """
    Update the upd_dict from SQL database. If table is not specified, uses column + 's' as table name

    :param column: column name
    :param table: table name
    :return:
    """
    if table is None:
        upd_dict[column + 's'] = list(map(lambda x: x[0],
                                          read_query(f'''SELECT {column} FROM {column}s''')))
    else:
        upd_dict[table] = list(map(lambda x: x[0], read_query(f'''SELECT {column} FROM {table}''')))


def update_pzl() -> None:
    """
    Update persons, zones and locations
    :return:
    """
    update('person')
    update('zone')
    update('location')


def add(fractions, c_weights, indices, info):
    """

    :param indices: Data class with indices
    :param info:  Data class with sampleinformation
    :param fractions: sand fractions
    :param c_weights: cumulative weights
    :return:
    """

    new_location = f'''
            INSERT INTO locations (location)
            VALUES ("{info.location}")
            '''
    execute_query(new_location)

    new_zone = f'''
    INSERT INTO zones (zone)
    VALUES ("{info.zone}")
    '''
    execute_query(new_zone)

    new_person = f'''
    INSERT INTO persons (person)
    VALUES ("{info.collector}"), ("{info.performer}")
    '''
    execute_query(new_person)

    new_sample = f''' INSERT INTO samples (sample, location_id, zone_id, latitude, longitude, sampling_date, collector, 
    analysis_date, performer, 'Mdφ', 'Mz', 'QDφ', 'σ_1', 'Skqφ', 'Sk_1', 'KG', 'SD')
    VALUES ( "{info.sample}", 
        "{get_id('location', info.location)}",
        "{get_id('zone', info.zone)}",
        "{info.lat}",
        "{info.lon}",
        "{info.sampling_date}",
        "{get_id('person', info.collector)}",
        "{date.today().strftime('%Y.%m.%d')}",
        "{get_id('person', info.performer)}",
        "{indices.MdPhi}",
        "{indices.Mz}",
        "{indices.QDPhi}",
        "{indices.sigma_1}",
        "{indices.SkqPhi}",
        "{indices.Sk_1}",
        "{indices.KG}",
        "{indices.SD}"
    )
    '''
    execute_query(new_sample)

    for i in range(len(fractions)):
        new_fractions = f'''
        INSERT INTO fractions (sample_id, fraction, weight)
        VALUES ("{get_id('sample', info.sample)}", "{fractions[i]}", "{c_weights[i]}")
        '''
        execute_query(new_fractions)
    update_pzl()


# create connection with SQL database.
connection = create_connection('GCDB.sqlite3')
db_from = '''
locations
    INNER JOIN samples USING (location_id)
    INNER JOIN zones USING (zone_id)
    INNER JOIN (SELECT person_id as pid, person as collector_name FROM persons) ON pid = samples.collector
    INNER JOIN (SELECT person_id as p, person as performer_name FROM persons) ON p = samples.performer
'''

tables = '''
locations
    INNER JOIN samples USING (location_id)
    INNER JOIN zones USING (zone_id)
    INNER JOIN (SELECT person_id as pid, person as collector_name FROM persons) ON pid = samples.collector
    INNER JOIN (SELECT person_id as p, person as performer_name FROM persons) ON p = samples.performer
'''

upd_dict = {
    'locations': (),
    'samples': (),
    'zones': (),
    'persons': (),
    'fractions': {}
}
