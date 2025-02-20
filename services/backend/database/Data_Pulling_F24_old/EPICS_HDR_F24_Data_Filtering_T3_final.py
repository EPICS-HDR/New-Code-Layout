import pandas as pd


##

def filter_water_chemicals(station_id, water_chemicals, data):
    """
    Filters water chemical data from a CSV file into multiple CSV files based on specified chemicals.

    Args:
    csv_file_path (str): The path to the main CSV file containing all station data.
    station_ids (list): List of station IDs to filter data for.
    water_chemicals (list): List of water chemicals to filter data for.
    """
    for chemical in water_chemicals:
        # Check if the chemical is present in the 'Parameter' column
        #Alternative (V2): 
        #if data['Parameter'].str.contains(chemical).any():
        #Alternative (V1): if data['Parameter'].values.find(chemical) != -1:
        #Alternative (Base): 
        if chemical in data['Parameter'].values:
        
            # Filter all rows where 'Parameter' matches the current chemical
            chemical_data = data[data['Parameter'] == chemical]
            
            # Remove rows where all specified numeric columns are zero or NaN
            numeric_columns = ['Min', 'Max', 'Median', 'Mean', 'Std Dev', 'Pct 10th', 'Pct 25th', 'Pct 75th', 'Pct 90th']
            filtered_data = chemical_data.loc[~(chemical_data[numeric_columns].fillna(0) == 0).all(axis=1)]

            # Define the output file name, replacing special characters for compatibility
            output_file_name = f"{chemical.replace(' ', '_').replace('(', '').replace(')', '')}.csv"
            # Save the filtered data to the output CSV
            filtered_data.to_csv(output_file_name, index=False)
            # Write to a single 'ph' file
            print(f"Filtered data for {chemical} saved to {output_file_name}")
    
    print("Filtering complete!")


def main():
    station_ids = [380990]
    csv_file_template = 'Water_Chemistry_Summary_{station_id}.csv' 
    water_chemicals = ['Phosphorus (Total) (P)', 'Phosphorus (Total Kjeldahl) (P)', 'Nitrate + Nitrite (N)', 
                       'Nitrate Forms Check', 'Nitrate + Nitrite (N) Dis', 'Nitrogen (Total Kjeldahl)', 'Nitrogen (TKN-Dissolved)', 
                       'Nitrogen (Total-Dis)', 'E.coli', 'Nitrogen (Total)',  'pH', 'Ammonia (N)', 'Ammonia (N)-Dissolved', 
                       'Ammonia Forms Check', 'Diss Ammonia TKN Check', 'Dissolved Phosphorus as P']
    for station_id in station_ids:
        csv_file_path = csv_file_template.format(station_id=station_id)
        data = pd.read_csv(csv_file_path)
        filter_water_chemicals(station_id, water_chemicals, data)

if __name__ == '__main__':
    main()