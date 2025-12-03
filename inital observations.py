import pandas as pd
import requests
import json

# Census API base URL
BASE_URL = "https://api.census.gov/data"

# You can get a free API key at: https://api.census.gov/data/key_signup.html
# For testing, you can leave it as None (limited requests)
#API_KEY = None # Replace with your key: "YOUR_API_KEY_HERE"
API_KEY = "116072db51d1d74ed352c58afeea90b570ea69ec"  # Replace with your key

def get_acs_data(year, variables, geography="state:*"):
    """
    Fetch data from Census ACS 1-Year API
    """
    url = f"{BASE_URL}/{year}/acs/acs1"
    
    params = {
        "get": ",".join(["NAME"] + variables),
        "for": geography
    }
    
    if API_KEY:
        params["key"] = API_KEY
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Convert to DataFrame
        df = pd.DataFrame(data[1:], columns=data[0])
        df['Year'] = year
        return df
    except Exception as e:
        print(f"Error fetching {year} data: {e}")
        return None

def main():
    """
    Pull state-level ACS data for 2019-2023:
    - Median Household Income
    - Unemployment Rate (via labor force status)
    - Educational Attainment
    """
    
    # ACS Variable Codes
    # See all variables: https://api.census.gov/data/2023/acs/acs1/variables.html
    variables = [
        "B19013_001E",  # Median household income
        "B23025_005E",  # Unemployed
        "B23025_003E",  # In labor force
        "B15003_017E",  # High school graduate
        "B15003_018E",  # GED or alternative
        "B15003_021E",  # Some college, less than 1 year
        "B15003_022E",  # Some college, 1+ years, no degree
        "B15003_023E",  # Associate's degree
        "B15003_024E",  # Bachelor's degree  
        "B15003_025E",  # Master's degree
        "B15003_001E",  # Total population 25+
    ]
    
    years = [2019, 2020, 2021, 2022, 2023]
    all_data = []
    
    print("Fetching ACS 1-Year data from Census API...")
    
    for year in years:
        print(f"  Downloading {year}...")
        df = get_acs_data(year, variables)
        if df is not None:
            all_data.append(df)
    
    if not all_data:
        print("No data retrieved. Check your internet connection or API key.")
        return
    
    # Combine all years
    combined = pd.concat(all_data, ignore_index=True)
    
    # Rename columns for clarity
    column_mapping = {
        "NAME": "State",
        "state": "FIPS",
        "Year": "Year",
        "B19013_001E": "Median_Household_Income",
        "B23025_005E": "Unemployed",
        "B23025_003E": "Labor_Force",
        "B15003_017E": "HS_Graduate",
        "B15003_018E": "GED",
        "B15003_021E": "Some_College_Less_1yr",
        "B15003_022E": "Some_College_1yr_Plus",
        "B15003_023E": "Associates_Degree",
        "B15003_024E": "Bachelors_Degree",
        "B15003_025E": "Masters_Degree",
        "B15003_001E": "Total_Pop_25_Plus"
    }
    
    combined = combined.rename(columns=column_mapping)
    
    # Calculate unemployment rate
    combined['Unemployed'] = pd.to_numeric(combined['Unemployed'], errors='coerce')
    combined['Labor_Force'] = pd.to_numeric(combined['Labor_Force'], errors='coerce')
    combined['Unemployment_Rate'] = (combined['Unemployed'] / combined['Labor_Force'] * 100).round(2)
    
    # Calculate education percentages
    edu_cols = ['HS_Graduate', 'GED', 'Some_College_Less_1yr', 'Some_College_1yr_Plus', 
                'Associates_Degree', 'Bachelors_Degree', 'Masters_Degree', 'Total_Pop_25_Plus']
    for col in edu_cols:
        combined[col] = pd.to_numeric(combined[col], errors='coerce')
    
    # Percentage with HS or higher
    combined['Pct_HS_or_Higher'] = (
        (combined['HS_Graduate'] + combined['GED'] + combined['Some_College_Less_1yr'] + 
            combined['Some_College_1yr_Plus'] + combined['Associates_Degree'] + 
            combined['Bachelors_Degree'] + combined['Masters_Degree']) / 
        combined['Total_Pop_25_Plus'] * 100
    ).round(2)
    
    # Percentage with Bachelor's or higher
    combined['Pct_Bachelors_or_Higher'] = (
        (combined['Bachelors_Degree'] + combined['Masters_Degree']) / 
        combined['Total_Pop_25_Plus'] * 100
    ).round(2)
    
    # Select final columns
    final_df = combined[[
        'State', 'FIPS', 'Year', 
        'Median_Household_Income', 
        'Unemployment_Rate',
        'Pct_HS_or_Higher',
        'Pct_Bachelors_or_Higher'
    ]].copy()
    
    # Add empty rows for 2024-2025
    states_2023 = final_df[final_df['Year'] == 2023][['State', 'FIPS']].copy()
    for year in [2024, 2025]:
        empty_year = states_2023.copy()
        empty_year['Year'] = year
        empty_year['Median_Household_Income'] = None
        empty_year['Unemployment_Rate'] = None
        empty_year['Pct_HS_or_Higher'] = None
        empty_year['Pct_Bachelors_or_Higher'] = None
        final_df = pd.concat([final_df, empty_year], ignore_index=True)
    
    # Sort
    final_df = final_df.sort_values(['State', 'Year']).reset_index(drop=True)
    
    # Save to CSV
    output_file = "state_socioeconomic_2019_2025.csv"
    final_df.to_csv(output_file, index=False)
    
    print(f"\n Success! Saved to: {output_file}")
    print(f"Total rows: {len(final_df)}")
    print(f"\nFirst few rows:")
    print(final_df.head(10))
    print(f"\nData coverage: 2019-2023 (real data), 2024-2025 (empty)")

if __name__ == "__main__":
    main()