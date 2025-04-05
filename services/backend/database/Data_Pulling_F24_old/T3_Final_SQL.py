import pandas as pd
import sqlite3

def create_chemical_tables(conn, water_chemicals):
    """
    Creates SQL tables for each chemical in the water_chemicals list.

    Args:
    conn: SQLite connection object
    water_chemicals (list): List of water chemicals to create tables for
    """
    cur = conn.cursor()
    for chemical in water_chemicals:
        table_name = f"chemical_{chemical.replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_')}"

        cur.execute(f"""CREATE TABLE IF NOT EXISTS {table_name}(
            station_id INTEGER,
            datetime TEXT,
            parameter TEXT,
            min REAL,
            max REAL,
            median REAL,
            mean REAL,
            std_dev REAL,
            pct_10th REAL,
            pct_25th REAL, 
            pct_75th REAL,
            pct_90th REAL,
            PRIMARY KEY(station_id, datetime)
        )""")

    conn.commit()

def filter_water_chemicals_to_sql(station_id, water_chemicals, data, conn):
    """
    Filters water chemical data from a CSV file into multiple CSV files based on specified chemicals.

    Args:
    csv_file_path (str): The path to the main CSV file containing all station data.
    station_ids (list): List of station IDs to filter data for.
    water_chemicals (list): List of water chemicals to filter data for.
    """

    """
    Filters water chemical data and stores it in SQL tables.

    Args:
    station_id (int): The station ID for the data
    water_chemicals (list): List of water chemicals to filter data for
    data (DataFrame): Pandas DataFrame containing the data
    conn: SQLite connection object
    """
    cur = conn.cursor()

    for chemical in water_chemicals:
        if chemical in data['Parameter'].values:
            chemical_data = data[data['Parameter'] == chemical]
            numeric_columns = ['Min', 'Max', 'Median', 'Mean', 'Std Dev', 'Pct 10th', 'Pct 25th', 'Pct 75th',
                               'Pct 90th']
            filtered_data = chemical_data.loc[~(chemical_data[numeric_columns].fillna(0) == 0).all(axis=1)]

            table_name = f"chemical_{chemical.replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_')}"

            for _, row in filtered_data.iterrows():
                # Prepare the insertion query
                query = f"""
                INSERT OR REPLACE INTO {table_name} 
                (station_id, datetime, parameter, min, max, median, mean, std_dev, pct_10th, pct_25th, pct_75th, pct_90th)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """

                cur.execute(query, (
                    station_id,
                    row.get('DateTime', ''),
                    row['Parameter'],
                    row.get('Min', 0),
                    row.get('Max', 0),
                    row.get('Median', 0),
                    row.get('Mean', 0),
                    row.get('Std Dev', 0),
                    row.get('Pct 10th', 0),
                    row.get('Pct 25th', 0),
                    row.get('Pct 75th', 0),
                    row.get('Pct 90th', 0)
                ))

            conn.commit()
            print(f"Data for {chemical} saved to SQL table {table_name}")

    print("SQL insertion complete!")

def main():
    station_ids = [380990]
    csv_file_template = 'Water_Chemistry_Summary_{station_id}.csv'

    water_chemicals = ['Phosphorus (Total) (P)', 'Phosphorus (Total Kjeldahl) (P)', 'Nitrate + Nitrite (N)',
                       'Nitrate Forms Check', 'Nitrate + Nitrite (N) Dis', 'Nitrogen (Total Kjeldahl)',
                       'Nitrogen (TKN-Dissolved)',
                       'Nitrogen (Total-Dis)', 'E.coli', 'Nitrogen (Total)', 'pH', 'Ammonia (N)',
                       'Ammonia (N)-Dissolved',
                       'Ammonia Forms Check', 'Diss Ammonia TKN Check', 'Dissolved Phosphorus as P']

    conn = sqlite3.connect('water_chemicals.db')
    create_chemical_tables(conn, water_chemicals)

    for station_id in station_ids:
        csv_file_path = csv_file_template.format(station_id=station_id)
        data = pd.read_csv(csv_file_path)
        filter_water_chemicals_to_sql(station_id, water_chemicals, data, conn)
    conn.close()


if __name__ == '__main__':
    main()