import requests
import pandas as pd
import re


def ParseDate(date_string):
    #passed format - '1997 Jan- 6 to Jan-10'
    #goal format - '2009-05-30'
    integers = re.findall('(\d+)', date_string) #['1997', '6', '10']
    words = re.findall('\s(\S+)-', date_string) #['Jan', 'Jan']
    year_start = integers[0] # '1997'
    year_end = integers[0] # '1997'
    day_start = integers[1] # '6'
    day_end = integers[2] # '10'
    month_start = words[0] # 'Jan'
    month_end = words[1] # 'Jan'

    
    # Translating month string to number
    month_dict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6,
                 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
    for key in month_dict.keys():
        month_start = month_start.replace(key, str(month_dict[key]))
        month_end = month_end.replace(key, str(month_dict[key]))
        
    # Check for crossing end of the year
    if month_end < month_start:
        year_end = str(int(year_end) + 1)
        
    start_date = '-'.join([year_start, month_start, day_start])
    end_date = '-'.join([year_end, month_end, day_end])
        
    return (start_date, end_date)

def ProgressMeter(current, total):
    #visualize progress of parsing data
    ten_percent = int(total / 10)
    percentage = current / ten_percent
    if int(percentage) == (percentage):
        print('#', end = '')


# Get data
target_url = 'https://www.eia.gov/dnav/ng/hist/rngwhhdD.htm'
df = pd.read_html(target_url)[5]
#print(df.head(10))

# Drop those nasty whitespace records, like row 6
df.dropna(thresh=2, inplace=True) 

# Drop column index
df.drop(0, inplace=True)
#print(df.head(10))


# Create DataFrame to hold the parsed data
df_result = pd.DataFrame(columns = ['Date', 'Month', 'Year', 'Price'])
filename = 'HH_Nat_Gas_Price_Daily.csv'

total_count = len(df[0])
print('Records to parse:', total_count)
print('Progress: ', end = '')
for row, record in df.iterrows():
    ProgressMeter(row, total_count)
    
    # Find start date and end date of the current record    
    date = record[0] 
    start_date, end_date = ParseDate(date)
    
    # Find the date range of the current record
    all_dates = pd.date_range(start_date, end_date)
    
    # Unpack current record
    for offset in range(0, 5):
        date_portion = all_dates[offset]
        df_result = df_result.append({'Date': date_portion.date(),
                                      'Day': date_portion.day,
                                     'Month': date_portion.month, 
                                     'Year': date_portion.year, 
                                     'Price':record[offset + 1]}, 
                                     ignore_index=True)
print(': Done!')
print('Saving file', filename)
print('-' * 25)
#print(df_result.head())
#print(df_result.tail())
df_result['Price'] = df_result['Price'].astype('float')
df_result[['Date', 'Price']].to_csv(filename, index = False)

# Save additional CSV with filters applied on dataset
filename = 'HH_Nat_Gas_Price_Monthly.csv'
print('Saving file', filename)
print('-' * 25)
df_result.dropna().drop_duplicates(subset=['Month', 'Year'])[['Date', 'Price']].to_csv(filename, index = False)
#print(df_result.dropna().drop_duplicates(subset=['Month', 'Year'])[['Date', 'Price']].head(13))

# Save additional CSV with filters applied on dataset
filename = 'HH_Nat_Gas_Price_Annual.csv'
print('Saving file', filename)
print('-' * 25)
df_result.dropna().drop_duplicates(subset=['Year'])[['Date', 'Price']].to_csv(filename, index = False)
#print(df_result.dropna().drop_duplicates(subset=['Year'])[['Date', 'Price']].head(22))
