import pandas as pd
import requests
import json

# # Census API base URL
# BASE_URL = "https://api.census.gov/data"

# # You can get a free API key at: https://api.census.gov/data/key_signup.html
# # For testing, you can leave it as None (limited requests)
# API_KEY = "116072db51d1d74ed352c58afeea90b570ea69ec" # Replace with your key: "YOUR_API_KEY_HERE"

# def get_acs_data(year, variables, geography="state:*"):
#     """
#     Fetch data from Census ACS 1-Year API
#     """
#     url = f"{BASE_URL}/{year}/acs/acs1"
    
#     params = {
#         "get": ",".join(["NAME"] + variables),
#         "for": geography
#     }
    
#     if API_KEY:
#         params["key"] = API_KEY
    
#     try:
#         response = requests.get(url, params=params)
#         response.raise_for_status()
#         data = response.json()
        
#         # Convert to DataFrame
#         df = pd.DataFrame(data[1:], columns=data[0])
#         df['Year'] = year
#         return df
#     except Exception as e:
#         print(f"Error fetching {year} data: {e}")
#         return None

# def get_income_by_education(year, geography="state:*"):
#     """
#     Fetch household income by educational attainment
#     Table B20004: Median Earnings in Past 12 Months by Educational Attainment
#     """
#     url = f"{BASE_URL}/{year}/acs/acs1"
    
#     # Income by education level for workers
#     variables = [
#         "B20004_001E",  # Total
#         "B20004_002E",  # Less than high school
#         "B20004_003E",  # High school graduate (includes equivalency)
#         "B20004_004E",  # Some college or associate's degree
#         "B20004_005E",  # Bachelor's degree
#         "B20004_006E",  # Graduate or professional degree
#     ]
    
#     params = {
#         "get": ",".join(["NAME"] + variables),
#         "for": geography
#     }
    
#     if API_KEY:
#         params["key"] = API_KEY
    
#     try:
#         response = requests.get(url, params=params)
#         response.raise_for_status()
#         data = response.json()
#         df = pd.DataFrame(data[1:], columns=data[0])
#         df['Year'] = year
#         return df
#     except Exception as e:
#         print(f"Error fetching income by education for {year}: {e}")
#         return None

# def main():
#     """
#     Pull state-level ACS data for 2019-2023:
#     - Average/Median Household Income by Educational Attainment
#     - Focus on vocational/associate's degrees vs other education levels
#     """
    
#     # ACS Variable Codes for household income by education
#     # Table B19037: Age of Householder by Household Income by Educational Attainment
#     variables = [
#         "B19013_001E",  # Overall median household income
#         # Median income by householder education (Table B19037)
#         "B19037_002E",  # Less than high school
#         "B19037_003E",  # High school graduate (includes equivalency)
#         "B19037_004E",  # Some college or associate's degree (VOCATIONAL)
#         "B19037_005E",  # Bachelor's degree or higher
#     ]
    
#     years = [2019, 2020, 2021, 2022, 2023]
#     all_data = []
    
#     print("Fetching ACS 1-Year data from Census API...")
    
#     for year in years:
#         print(f"  Downloading {year}...")
#         df = get_acs_data(year, variables)
#         if df is not None:
#             all_data.append(df)
    
#     if not all_data:
#         print("No data retrieved. Check your internet connection or API key.")
#         return
    
#     # Combine all years
#     combined = pd.concat(all_data, ignore_index=True)
    
#     # Rename columns for clarity
#     column_mapping = {
#         "NAME": "State",
#         "state": "FIPS",
#         "Year": "Year",
#         "B19013_001E": "Median_Household_Income",
#         "B23025_005E": "Unemployed",
#         "B23025_003E": "Labor_Force",
#         "B15003_017E": "HS_Graduate",
#         "B15003_018E": "GED",
#         "B15003_021E": "Some_College_Less_1yr",
#         "B15003_022E": "Some_College_1yr_Plus",
#         "B15003_023E": "Associates_Degree",
#         "B15003_024E": "Bachelors_Degree",
#         "B15003_025E": "Masters_Degree",
#         "B15003_001E": "Total_Pop_25_Plus"
#     }
    
#     combined = combined.rename(columns=column_mapping)
    
#     # Calculate unemployment rate
#     combined['Unemployed'] = pd.to_numeric(combined['Unemployed'], errors='coerce')
#     combined['Labor_Force'] = pd.to_numeric(combined['Labor_Force'], errors='coerce')
#     combined['Unemployment_Rate'] = (combined['Unemployed'] / combined['Labor_Force'] * 100).round(2)
    
#     # Calculate education percentages
#     edu_cols = ['HS_Graduate', 'GED', 'Some_College_Less_1yr', 'Some_College_1yr_Plus', 
#                 'Associates_Degree', 'Bachelors_Degree', 'Masters_Degree', 'Total_Pop_25_Plus']
#     for col in edu_cols:
#         combined[col] = pd.to_numeric(combined[col], errors='coerce')
    
#     # Percentage with HS or higher
#     combined['Pct_HS_or_Higher'] = (
#         (combined['HS_Graduate'] + combined['GED'] + combined['Some_College_Less_1yr'] + 
#             combined['Some_College_1yr_Plus'] + combined['Associates_Degree'] + 
#             combined['Bachelors_Degree'] + combined['Masters_Degree']) / 
#         combined['Total_Pop_25_Plus'] * 100
#     ).round(2)
    
#     # Percentage with Bachelor's or higher
#     combined['Pct_Bachelors_or_Higher'] = (
#         (combined['Bachelors_Degree'] + combined['Masters_Degree']) / 
#         combined['Total_Pop_25_Plus'] * 100
#     ).round(2)
    
#     # Select final columns
#     final_df = combined[[
#         'State', 'FIPS', 'Year', 
#         'Median_Household_Income', 
#         'Unemployment_Rate',
#         'Pct_HS_or_Higher',
#         'Pct_Bachelors_or_Higher'
#     ]].copy()
    
#     # Add empty rows for 2024-2025
#     states_2023 = final_df[final_df['Year'] == 2023][['State', 'FIPS']].copy()
#     for year in [2024, 2025]:
#         empty_year = states_2023.copy()
#         empty_year['Year'] = year
#         empty_year['Median_Household_Income'] = None
#         empty_year['Unemployment_Rate'] = None
#         empty_year['Pct_HS_or_Higher'] = None
#         empty_year['Pct_Bachelors_or_Higher'] = None
#         final_df = pd.concat([final_df, empty_year], ignore_index=True)
    
#     # Sort
#     final_df = final_df.sort_values(['State', 'Year']).reset_index(drop=True)
    
#     # Save to CSV
#     output_file = "state_socioeconomic_2019_2025.csv"
#     final_df.to_csv(output_file, index=False)
    
#     print(f"\n Success! Saved to: {output_file}")
#     print(f"Total rows: {len(final_df)}")
#     print(f"\nFirst few rows:")
#     print(final_df.head(10))
#     print(f"\nData coverage: 2019-2023 (real data), 2024-2025 (empty)")

# if __name__ == "__main__":
#     main()

import pandas as pd
import requests

# Census API base URL
BASE_URL = "https://api.census.gov/data"

# Add your Census API key here
API_KEY = "116072db51d1d74ed352c58afeea90b570ea69ec"

def get_acs_data(year, variables, geography="state:*"):
    """
    Fetch data from Census ACS 1-Year API
    Focus: Household income broken down by householder's educational attainment
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
    - Household Income by Educational Attainment
    - Focus on vocational/associate's degrees vs other education levels
    """
    
    # ACS Variable Codes for household income by education
    # Table B19037: Median Household Income by Educational Attainment
    variables = [
        "B19013_001E",  # Overall median household income
        "B19037_002E",  # Less than high school
        "B19037_003E",  # High school graduate (includes equivalency)
        "B19037_004E",  # Some college or associate's degree (VOCATIONAL)
        "B19037_005E",  # Bachelor's degree or higher
    ]
    
    # Note: 2020 ACS 1-year was not released due to COVID-19 data collection issues
    years = [2019, 2021, 2022, 2023]
    all_data = []
    
    print("Fetching ACS 1-Year data from Census API...")
    print("Note: 2020 data not available (Census did not release 1-year estimates)")
    
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
        "B19013_001E": "Overall_Median_Household_Income",
        "B19037_002E": "Median_Income_LessThan_HS",
        "B19037_003E": "Median_Income_HS_Graduate",
        "B19037_004E": "Median_Income_SomeCollege_AssociateDegree",
        "B19037_005E": "Median_Income_Bachelors_Plus",
    }
    
    combined = combined.rename(columns=column_mapping)
    
    # Convert income columns to numeric
    income_cols = [
        'Overall_Median_Household_Income',
        'Median_Income_LessThan_HS',
        'Median_Income_HS_Graduate', 
        'Median_Income_SomeCollege_AssociateDegree',
        'Median_Income_Bachelors_Plus'
    ]
    
    for col in income_cols:
        combined[col] = pd.to_numeric(combined[col], errors='coerce')
    
    # Calculate income premium for vocational/associate's vs HS only
    combined['Vocational_Premium_vs_HS'] = (
        combined['Median_Income_SomeCollege_AssociateDegree'] - 
        combined['Median_Income_HS_Graduate']
    ).round(0)
    
    combined['Vocational_Premium_Pct_vs_HS'] = (
        (combined['Median_Income_SomeCollege_AssociateDegree'] / 
         combined['Median_Income_HS_Graduate'] - 1) * 100
    ).round(2)
    
    # Calculate gap between vocational and bachelor's
    combined['Bachelors_Premium_vs_Vocational'] = (
        combined['Median_Income_Bachelors_Plus'] - 
        combined['Median_Income_SomeCollege_AssociateDegree']
    ).round(0)
    
    # Select final columns
    final_df = combined[[
        'State', 'FIPS', 'Year',
        'Overall_Median_Household_Income',
        'Median_Income_LessThan_HS',
        'Median_Income_HS_Graduate',
        'Median_Income_SomeCollege_AssociateDegree',
        'Median_Income_Bachelors_Plus',
        'Vocational_Premium_vs_HS',
        'Vocational_Premium_Pct_vs_HS',
        'Bachelors_Premium_vs_Vocational'
    ]].copy()
    
    # Add 2020 rows with null values (data not collected)
    states_2019 = final_df[final_df['Year'] == 2019][['State', 'FIPS']].copy()
    empty_2020 = states_2019.copy()
    empty_2020['Year'] = 2020
    for col in final_df.columns:
        if col not in ['State', 'FIPS', 'Year']:
            empty_2020[col] = None
    
    # Add empty rows for 2024-2025
    states_2023 = final_df[final_df['Year'] == 2023][['State', 'FIPS']].copy()
    empty_rows = []
    for year in [2024, 2025]:
        empty_year = states_2023.copy()
        empty_year['Year'] = year
        for col in final_df.columns:
            if col not in ['State', 'FIPS', 'Year']:
                empty_year[col] = None
        empty_rows.append(empty_year)
    
    # Combine everything
    final_df = pd.concat([final_df, empty_2020] + empty_rows, ignore_index=True)
    
    # Sort
    final_df = final_df.sort_values(['State', 'Year']).reset_index(drop=True)
    
    # Save to CSV
    output_file = "household_income_by_education_2019_2025.csv"
    final_df.to_csv(output_file, index=False)
    
    print(f"\n Success! Saved to: {output_file}")
    print(f"Total rows: {len(final_df)}")
    print(f"\n Sample data - California:")
    sample_state = final_df[final_df['State'].str.contains('California', na=False)].head(6)
    if not sample_state.empty:
        print(sample_state.to_string(index=False))
    
    print(f"\n\n💡 KEY INSIGHTS:")
    print("=" * 70)
    print("This dataset shows how VOCATIONAL/ASSOCIATE'S DEGREE education")
    print("impacts household income compared to:")
    print("  • High school only")
    print("  • Bachelor's degree+")
    print("\nColumns explained:")
    print("  • Median_Income_SomeCollege_AssociateDegree = Vocational schooling")
    print("  • Vocational_Premium_vs_HS = Extra income vs HS diploma ($)")
    print("  • Vocational_Premium_Pct_vs_HS = Percentage increase vs HS (%)")
    print("  • Bachelors_Premium_vs_Vocational = Income gap to bachelor's ($)")
    print("\nNote: 2020 data is empty (Census did not release 1-year estimates)")
    print("=" * 70)

if __name__ == "__main__":
    main()