
# coding: utf-8

# In[25]:


import requests
import pandas as pd
import re

from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.graph_objs as go
import cufflinks as cf
get_ipython().run_line_magic('matplotlib', 'inline')

#for notebook
init_notebook_mode(connected=True)

# For offline use
cf.go_offline()


# In[2]:


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
        
    return (start_date, end_date, month_start, '-'.join([month_start, day_start]))

def ProgressMeter(current, total):
    ten_percent = int(total / 10)
    percentage = current / ten_percent
    if int(percentage) == (percentage):
        print('#', end = '')


# In[3]:


# Get data
target_url = 'https://www.eia.gov/dnav/ng/hist/rngwhhdD.htm'
df = pd.read_html(target_url)[5]
df.head(10)


# In[4]:


# Drop those nasty whitespace records, like row 6
df.dropna(thresh=2, inplace=True) 

# Drop column index
df.drop(0, inplace=True)

df.head(10)


# In[5]:


# Figure out start date and end date of one row of the dataset
date = df[0][1]
print(date)


# In[6]:


start_date = ParseDate(date)[0]
end_date = ParseDate(date)[1]
print(start_date, end_date, sep = '\n')


# In[7]:


# Figure out date range of one row
all_dates = pd.date_range(start_date, end_date)
print(all_dates)


# In[8]:


for row, record in df.iterrows():
    # Find start date and end date of the current record
    date = record[0]
    start_date = ParseDate(date)[0]
    end_date = ParseDate(date)[1]
    print(start_date, end_date, sep = '\n')
    
    # Find the date range of the current record
    all_dates = pd.date_range(start_date, end_date)
    
    print('-'*25)
    print('Iteration result:')
    print('-'*25)
    #unpacking current record
    for offset in range(0, 5):
        print(all_dates[offset].date(), record[offset + 1], sep = ' -- ')
    break
print('-'*25)
print('Data check, as in row 1:')
print('-'*25)
print(record)


# In[9]:


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
    start_date = ParseDate(date)[0]
    end_date = ParseDate(date)[1]
    
    # Find the date range of the current record
    all_dates = pd.date_range(start_date, end_date)
    
    #unpacking current record
    for offset in range(0, 5):
        df_result = df_result.append({'Date':all_dates[offset].date(),
                                      'Day': all_dates[offset].day,
                                     'Month':all_dates[offset].month, 
                                     'Year':all_dates[offset].year, 
                                     'Price':record[offset + 1]}, 
                                     ignore_index=True)
print(': Done!')
print('Saving file', filename)
print('-' * 25)
print(df_result.head())
print(df_result.tail())
df_result['Price'] = df_result['Price'].astype('float')
df_result[['Date', 'Price']].to_csv(filename, index = False)


# In[10]:


filename = 'HH_Nat_Gas_Price_Monthly.csv'
print('Saving file', filename)
df_result.dropna().drop_duplicates(subset=['Month', 'Year'])[['Date', 'Price']].to_csv(filename, index = False)
print(df_result.dropna().drop_duplicates(subset=['Month', 'Year'])[['Date', 'Price']].head(13))


# In[11]:


filename = 'HH_Nat_Gas_Price_Annual.csv'
print('Saving file', filename)
df_result.dropna().drop_duplicates(subset=['Year'])[['Date', 'Price']].to_csv(filename, index = False)
print(df_result.dropna().drop_duplicates(subset=['Year'])[['Date', 'Price']].head(22))


# In[31]:


data = [go.Scatter(x=df_result['Date'], y=df_result['Price'])]

layout = go.Layout(
    title='Henry Hub Natural Gas Spot Price',
    yaxis=dict(title='Price'),
    xaxis=dict(title='Years')
)

fig = go.Figure(data=data, layout=layout)


iplot(fig)

