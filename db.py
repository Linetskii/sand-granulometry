import sqlite3
from os import path, getcwd
from datetime import date


class SingletonMetaclass(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class DataBase(metaclass=SingletonMetaclass):
    __connection = None

    def __init__(self):
        DataBase.__connection = self.__create_connection('GCDB.sqlite3')
        self.__create_db()
        self.__headers = ('Collector_name', 'Sampling_date', 'Performer_name', 'Analysis_date', 'Sample', 'Location',
                          'Zone', 'Latitude', 'Longitude', 'Mdφ', 'Mz', 'QDφ', 'σ_1', 'Skqφ', 'Sk_1', 'KG', 'SD')

    @property
    def headers(self):
        return self.__headers

    @staticmethod
    def __create_connection(pth: str):
        """
        Create the connection with SQL database

        :param pth: name of database file
        :return: connection with database
        """
        con = None
        try:
            print('Connection to sqlite DB...')
            con = sqlite3.connect(path.join(getcwd(), pth))
        except sqlite3.Error as e:
            print(f"The error '{e}' occurred")
        return con

    def run_query(self, query: str):
        """
        Execute query. SELECT query must return the result

        :param query: SQL query
        :return: selected items (only for SELECT query)
        """
        if not self.__connection:
            pass
        cursor = self.__connection.cursor()
        try:
            print(f"Run query...")
            cursor.execute(query)
            # SELECT query must return the result of execution
            if query.lstrip().startswith("SELECT"):
                return cursor.fetchall()
            else:
                self.__connection.commit()
        except sqlite3.Error as e:
            print(f"Can`t run the query. The error '{e}' occurred")

    def __create_db(self) -> None:
        """create locations, zones, persons, samples and fractions tables"""
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
        self.run_query(create_locations_table)
        self.run_query(create_zones_table)
        self.run_query(create_persons_table)
        self.run_query(create_fractions_table)
        self.run_query(create_samples_table)

    def get_id(self, item: str, val: str) -> str:
        """
        Get desired id from SQL database.
        Val must be in column "item" of table "item"+"s" with id in "item"+"_id" column.

        :param item: column name with desired value
        :param val: value to search
        :return: item_id of value in items table
        """
        query = f'''
        SELECT {item}_id
        FROM {item}s
        WHERE {item} = "{val}"
        '''
        return self.run_query(query)[0][0]

    # TODO: rename methods below adding the changeable entities to method-name
    def update(self, column: str, table: str = None) -> tuple:
        """
        Update the upd_dict from SQL database. If table is not specified, uses column + 's' as table name

        :param column: column name
        :param table: table name
        """
        if table is None:
            return tuple(map(lambda x: x[0], self.run_query(f'''SELECT {column} FROM {column}s''')))
        else:
            return tuple(map(lambda x: x[0], self.run_query(f'''SELECT {column} FROM {table}''')))

    def add(self, fract, c_weights, indices, info) -> None:
        """
        Add sample into database

        :param indices: Data class with indices
        :param info:  Data class with sample information
        :param fract: sand fractions iterable
        :param c_weights: cumulative weights iterable
        """
        # Add location to locations table
        new_location = f'''
        INSERT INTO locations (location)
        VALUES ("{info.location}")
        '''
        self.run_query(new_location)
        # Add zone to 'zones' table
        new_zone = f'''
        INSERT INTO zones (zone)
        VALUES ("{info.zone}")
        '''
        self.run_query(new_zone)
        # Add person to persons table
        new_person = f'''
        INSERT INTO persons (person)
        VALUES ("{info.collector}"), ("{info.performer}")
        '''
        self.run_query(new_person)
        # Add sample to sample table
        new_sample = f''' INSERT INTO samples (sample, location_id, zone_id, latitude, longitude, sampling_date,
        collector, analysis_date, performer, 'Mdφ', 'Mz', 'QDφ', 'σ_1', 'Skqφ', 'Sk_1', 'KG', 'SD')
        VALUES ( 
            "{info.sample}", 
            "{self.get_id('location', info.location)}",
            "{self.get_id('zone', info.zone)}",
            "{info.lat}",
            "{info.lon}",
            "{info.sampling_date}",
            "{self.get_id('person', info.collector)}",
            "{date.today().strftime('%Y-%m-%d')}",
            "{self.get_id('person', info.performer)}",
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
        self.run_query(new_sample)
        # Add fractions and weights into fractions table
        for i in range(len(fract)):
            new_fractions = f'''
            INSERT INTO fractions (sample_id, fraction, weight)
            VALUES ("{self.get_id('sample', info.sample)}", "{fract[i]}", "{c_weights[i]}")
            '''
            self.run_query(new_fractions)

    def delete_samples(self, samples) -> None:
        """
        Delete samples and associated fractions from database
        :param samples: tuple of sample names
        """
        for i in samples:
            query_fr = f"""
            DELETE FROM fractions
            WHERE sample_id = "{self.get_id('sample', i)}"
            """
            self.run_query(query_fr)
        query_s = f"""
        DELETE FROM samples
        WHERE sample = "{'" OR sample = "'.join(samples)}"
        """
        self.run_query(query_s)


class CFG(metaclass=SingletonMetaclass):
    """
    Config class.
    """
    __slots__ = ('sep', 'rnd_ind', 'rnd_frac', 'def_fract')

    def __init__(self):
        self.sep = None
        self.rnd_ind = None
        self.rnd_frac = None
        self.def_fract = None
        self.__update()
        print(self.sep, self.rnd_ind, self.rnd_frac, self.def_fract)

    def __update(self) -> None:
        """
        Update from config.txt
        """
        with open('config.txt', 'r') as config:
            self.sep = config.readline().split(' = ')[1][1:-2]
            self.rnd_ind = int(config.readline().split(' = ')[1])
            self.rnd_frac = int(config.readline().split(' = ')[1])
            self.def_fract = config.readline().split(' = ')[1]
        print(self.sep, self.rnd_ind, self.rnd_frac, self.def_fract)

    def apply_settings(self, sep, rnd_ind, rnd_frac, def_fract) -> None:
        """
        Write settings to config.txt
        """
        with open('config.txt', 'w') as config:
            config.write(f"sep = \'{sep}\'\nrnd_ind = {rnd_ind}\n"
                         f"rnd_frac = {rnd_frac}\ndef_fract = {def_fract}")
        self.__update()
