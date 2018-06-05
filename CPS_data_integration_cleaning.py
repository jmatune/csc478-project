# CSC 478 Project
# Data Integration, Cleaning and Preprocessing Code


#  Code to combine school level data with neighborhood level demographic data
#  Used shapely to assign neighborhoods to schools based on lat-long
#  Joined demographic neighborhood to school information based on neighborhood name

import json
import urllib3
import re
from shapely.geometry import Polygon, Point
import pandas as pd

# Open URL and consume json
pool = urllib3.PoolManager()
source = pool.request('GET', 'https://data.cityofchicago.org/api/views/igwz-8jzy/rows.json')
raw_lines = source.data
raw_dict = json.loads(raw_lines)

# JSON is structured with two main sections: 'meta' and 'data'
# All geo boundaries are stored within 'data' section, which is a list of lists, with one entry per neighborhood
# Coordinates are stored starting at 9th entry (counting from 1). Community name is 4th from end.

# Goal is to iterate through list entries and return the name with coordinates as list of tuples (shapely format)


# Take list entry for neighborhood
# Return neighborhood name and shapely poly object
def get_poly(geo_list):
    # Retrieve name
    name = geo_list[len(geo_list)-4]

    # Retrieve coordinate tuples
    geo_string = geo_list[8]
    coord_string = geo_string[16:len(geo_string)-3]  # strips unnecessary junk at head and tail
    poly_tuples = list([list(map(str, coords.lstrip().split(' '))) for coords in coord_string.split(',')])

    #  define regex string to parse out non-numeric characters
    non_decimal = re.compile(r'[^\d.]+')

    #  loop through coordinate pairs to remove problem characters, then transform to tuple
    for n, poly_tup in enumerate(poly_tuples):
        for i, value in enumerate(poly_tup):
            poly_tup[i] = float(non_decimal.sub('', value))
        poly_tuples[n] = tuple(poly_tuples[n])
    return name, poly_tuples


# Return neighborhood name by doing point-in-polygon check with lat/long
def get_name(lat, long):
    point_tuple = Point(float(lat)*-1, float(long))
    n_name = 'Not Found'
    for key_name in poly_dict.keys():
        n_poly = poly_dict[key_name]

        if point_tuple.within(n_poly):
            n_name = key_name
    return n_name


#  create shapely polygons from json coordinate strings
poly_dict = {}
for item in raw_dict['data']:
    neighborhood, poly = get_poly(item)
    shapely_poly = Polygon(poly)
    poly_dict[neighborhood] = shapely_poly

#  read in school data
hs_data = pd.read_csv('school_lib.csv', sep=',', header=0)
hs_data['Neighborhood Name'] = 'None'

for row in range(hs_data.shape[0]):
    hs_data['Neighborhood Name'].iloc[row] = get_name(hs_data['School_Longitude.1'].iloc[row],
                                                      hs_data['School_Latitude.1'].iloc[row])

#  Read in census data for non-english language
census_lang = pd.read_csv('Census_Neighborhood_Language.csv', sep=',', header=0)
census_lang.set_index(['NEIGHBORHOOD'], inplace=True)

#  join to school data
hs_data_lang = hs_data.join(census_lang, on='Neighborhood Name')

census_econ = pd.read_csv('Census_Socio_Econ.csv', sep=',', header=0)
census_econ.set_index(['NEIGHBORHOOD'], inplace=True)

#  join to school data
hs_data_lang_socio = hs_data_lang.join(census_econ, on='Neighborhood Name')

#  write dataframe to csv
hs_data_lang_socio.to_csv('hs_data_all_fields.csv')


################################################################################################
# Adding Library Location data to CPS dataset


# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np


# In[2]:


import json as js
from shapely import geometry


# In[3]:


json_file_s = open ('C:/Users/vishn/Desktop/Machine Learning/Project/schools.json')
json_string_s = json_file_s.read()
json_schools = js.loads(json_string_s)
json_file_l = open ('C:/Users/vishn/Desktop/Machine Learning/Project/libraries.json')
json_string_l = json_file_l.read()
json_libraries = js.loads(json_string_l)
school=pd.read_csv('C:/Users/vishn/Desktop/Machine Learning/Project/schools.csv')
school['School_ID']=school['School_ID'].astype(int)


# In[4]:


from math import sin, cos, sqrt, atan2, radians


# In[5]:


df=pd.DataFrame(columns=['School_ID','lib_cnt'])
for i in range(0,len(json_schools['data'])):
    R = 6373.0
    if json_schools['data'][i][14]==u'HS':
        lon=radians(float(json_schools['data'][i][75]))
        lat=radians(float(json_schools['data'][i][76]))
        cnt=0
        school_id=json_schools['data'][i][8]
        for j in range(0,len(json_libraries['data'])):
            lon2=radians(float(json_libraries['data'][j][18][1]))
            lat2=radians(float(json_libraries['data'][j][18][2]))
            dlon = lon2 - lon
            dlat = lat2 - lat
            a = (sin(dlat/2))**2 + cos(lat) * cos(lat2) * (sin(dlon/2))**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            distance = R * c * 0.621371
            if distance<=0.5:
                cnt+=1
            else:
                cnt+=0
        newrow=pd.DataFrame([[school_id,cnt],], columns=['School_ID','lib_cnt'])
        df=df.append(newrow)
df['School_ID']=df['School_ID'].astype(int)


# In[6]:


school_lib=school.merge(df,on='School_ID')


# In[7]:


school_lib.to_csv('C:/Users/vishn/Desktop/Machine Learning/Project/school_lib.csv')









################################################################################################
# Preprocessing integrated dataset



# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
data=pd.read_csv('hs_data_all_fields.csv', index_col=0)
data.drop(labels=['Freshmen_On_Track_CPS_Pct_Year_2','Graduation_4_Year_School_Pct_Year_2','Graduation_4_Year_School_Pct_Year_1','Graduation_5_Year_School_Pct_Year_1','College_Enrollment_CPS_Pct_Year_2','College_Enrollment_School_Pct_Year_1','College_Persistence_CPS_Pct_Year_2','Mobility_Rate_Pct','College_Persistence_School_Pct_Year_1','College_Persistence_CPS_Pct_Year_1','College_Enrollment_CPS_Pct_Year_1','Graduation_5_Year_CPS_Pct_Year_1','Graduation_5_Year_CPS_Pct_Year_2','Graduation_4_Year_CPS_Pct_Year_1','Graduation_4_Year_CPS_Pct_Year_2','Freshmen_On_Track_School_Pct_Year_1','Freshmen_On_Track_CPS_Pct_Year_1','Unnamed: 0.1','School_Hours','Legacy_Unit_ID','Finance_ID','Short_Name','Summary','Primary_Category','Is_High_School','Is_Middle_School','Is_Elementary_School','Is_Pre_School','Administrator_Title','Administrator','Phone','Secondary_Contact_Title','Secondary_Contact','Address','City','State','Zip','Fax','Freshman_Start_End_Time','After_School_Hours','Earliest_Drop_Off_Time','Significantly_Modified','Blue_Ribbon_Award_Year','Spot_Light_Award_Year','Improvement_Award_Year','Excellence_Award_Year','Hard_Of_Hearing','Mean_ACT','College_Enrollment_Rate_Mean','School_Year','Progress_Report_Year','Graduation_Rate_Mean','Visual_Impairments','School_Latitude','Classroom_Languages','CPS_School_Profile','Website','Facebook','Twitter','Youtube','Pinterest','Attendance_Boundaries','Grades_Offered_All','Grades_Offered','Student_Count_Native_American','Student_Count_Other_Ethnicity','Student_Count_Asian_Pacific_Islander','Student_Count_Multi','Student_Count_Hawaiian_Pacific_Islander','Student_Count_Ethnicity_Not_Available','Statistics_Description','Demographic_Description','PreK_School_Day','Kindergarten_School_Day','PreSchool_Inclusive','Preschool_Instructional','School_Longitude','School_Longitude','Rating_Statement','Classification_Description','Third_Contact_Title','Third_Contact_Name','Fourth_Contact_Title','Fourth_Contact_Name','Fifth_Contact_Title','Fifth_Contact_Name','Sixth_Contact_Title','Sixth_Contact_Name','Seventh_Contact_Title','Seventh_Contact_Name','Location','Excelerate_Award_Gold_Year','Student_Growth_Description','Growth_Reading_Grades_Tested_Pct_ES','Growth_Reading_Grades_Tested_Label_ES','Growth_Math_Grades_Tested_Pct_ES','Growth_Math_Grades_Tested_Label_ES','Student_Attainment_Description','Attainment_Reading_Pct_ES','Attainment_Reading_Lbl_ES','Attainment_Math_Pct_ES','Attainment_Math_Lbl_ES','Culture_Climate_Description','School_Survey_Student_Response_Rate_Avg_Pct','School_Survey_Teacher_Response_Rate_Avg_Pct','Healthy_School_Certification','Healthy_School_Certification_Description','School_Survey_Student_Response_Rate_Pct','School_Survey_Teacher_Response_Rate_Pct','Creative_School_Certification','Creative_School_Certification_Description','NWEA_Reading_Growth_Grade_3_Pct','NWEA_Reading_Growth_Grade_3_Lbl','NWEA_Reading_Growth_Grade_4_Pct','NWEA_Reading_Growth_Grade_4_Lbl','NWEA_Reading_Growth_Grade_5_Pct','NWEA_Reading_Growth_Grade_5_Lbl','NWEA_Reading_Growth_Grade_6_Pct','NWEA_Reading_Growth_Grade_6_Lbl','NWEA_Reading_Growth_Grade_7_Pct','NWEA_Reading_Growth_Grade_7_Lbl','NWEA_Reading_Growth_Grade_8_Pct','NWEA_Reading_Growth_Grade_8_Lbl','NWEA_Math_Growth_Grade_3_Pct','NWEA_Math_Growth_Grade_3_Lbl','NWEA_Math_Growth_Grade_4_Pct','NWEA_Math_Growth_Grade_4_Lbl','NWEA_Math_Growth_Grade_5_Pct','NWEA_Math_Growth_Grade_5_Lbl','NWEA_Math_Growth_Grade_6_Pct','NWEA_Math_Growth_Grade_6_Lbl','NWEA_Math_Growth_Grade_7_Pct','NWEA_Math_Growth_Grade_7_Lbl','NWEA_Math_Growth_Grade_8_Pct','NWEA_Math_Growth_Grade_8_Lbl','NWEA_Reading_Attainment_Grade_2_Pct','NWEA_Reading_Attainment_Grade_2_Lbl','NWEA_Reading_Attainment_Grade_3_Pct','NWEA_Reading_Attainment_Grade_3_Lbl','NWEA_Reading_Attainment_Grade_4_Pct','NWEA_Reading_Attainment_Grade_4_Lbl','NWEA_Reading_Attainment_Grade_5_Pct','NWEA_Reading_Attainment_Grade_5_Lbl','NWEA_Reading_Attainment_Grade_6_Pct','NWEA_Reading_Attainment_Grade_6_Lbl','NWEA_Reading_Attainment_Grade_7_Pct','NWEA_Reading_Attainment_Grade_7_Lbl','NWEA_Reading_Attainment_Grade_8_Pct','NWEA_Reading_Attainment_Grade_8_Lbl','NWEA_Math_Attainment_Grade_2_Pct','NWEA_Math_Attainment_Grade_2_Lbl','NWEA_Math_Attainment_Grade_3_Pct','NWEA_Math_Attainment_Grade_3_Lbl','NWEA_Math_Attainment_Grade_4_Pct','NWEA_Math_Attainment_Grade_4_Lbl','NWEA_Math_Attainment_Grade_5_Pct','NWEA_Math_Attainment_Grade_5_Lbl','NWEA_Math_Attainment_Grade_6_Pct','NWEA_Math_Attainment_Grade_6_Lbl','NWEA_Math_Attainment_Grade_7_Pct','NWEA_Math_Attainment_Grade_7_Lbl','NWEA_Math_Attainment_Grade_8_Pct','NWEA_Math_Attainment_Grade_8_Lbl','Suspensions_Per_100_Students_Avg_Pct','Misconducts_To_Suspensions_Avg_Pct','Average_Length_Suspension_Year_1_Pct','Average_Length_Suspension_Year_2_Pct','Average_Length_Suspension_Avg_Pct','Behavior_Discipline_Year_1','Behavior_Discipline_Year_2','Student_Attendance_Avg_Pct','Teacher_Attendance_Avg_Pct','One_Year_Dropout_Rate_Avg_Pct','Other_Metrics_Year_1','Other_Metrics_Year_2','Growth_ACT_Grade_11_Lbl','Attainment_ACT_Grade_11_Lbl','Progress_Toward_Graduation_Year_1','Progress_Toward_Graduation_Year_2','State_School_Report_Card_URL','Chronic_Truancy_Pct','Empty_Progress_Report_Message','School_Survey_Rating_Description','Supportive_School_Award_Desc','Parent_Survey_Results_Year','School_Latitude.1','School_Longitude.1','Transportation_Bus','Transportation_El','Transportation_Metra'], axis=1,inplace=True)
data.set_index('School_ID', inplace=True)
name=data['Long_Name']
data.drop(labels='Long_Name', axis=1, inplace=True)
data=data[-data['Graduation_Rate_School'].isna()]
data.describe(include='all').T


# In the above step we are deleting irrelevant column names, subsetting the data to school that have graduation rate value filled out, separating names of schools for future use if needed, changing index to school id.

# Next step is to create change values from fields that have year 1 and year 2 and drop original variables

# In[2]:


data['Suspensions_Per_100_Students_Change']=data['Suspensions_Per_100_Students_Year_1_Pct']-data['Suspensions_Per_100_Students_Year_2_Pct']
data['Misconducts_To_Suspensions_Change']=data['Misconducts_To_Suspensions_Year_1_Pct']-data['Misconducts_To_Suspensions_Year_2_Pct']
data['Student_Attendance_Change']=data['Student_Attendance_Year_1_Pct']-data['Student_Attendance_Year_2_Pct']
data['Teacher_Attendance_Change']=data['Teacher_Attendance_Year_1_Pct']-data['Teacher_Attendance_Year_2_Pct']
data['One_Year_Dropout_Rate_Change']=data['One_Year_Dropout_Rate_Year_1_Pct']-data['One_Year_Dropout_Rate_Year_2_Pct']
data.drop(labels=['College_Enrollment_School_Pct_Year_2','Graduation_5_Year_School_Pct_Year_2','Suspensions_Per_100_Students_Year_1_Pct','Suspensions_Per_100_Students_Year_2_Pct','Misconducts_To_Suspensions_Year_1_Pct','Misconducts_To_Suspensions_Year_2_Pct','Student_Attendance_Year_1_Pct','Student_Attendance_Year_2_Pct','Teacher_Attendance_Year_1_Pct','Teacher_Attendance_Year_2_Pct','One_Year_Dropout_Rate_Year_1_Pct','One_Year_Dropout_Rate_Year_2_Pct'],axis=1,inplace=True)


# Following step fills in null values:
#
# average for missing values of ACT Score, college enrollment rate, and other percent values related to school or college performance
#
# zeroes for rates of change from previous year; we are assuming that schools that had missing values for suspension, misconduct, teacher attendance and one year drop out rates, had no changces from 2015 to 2016
#
# U for unknown for categorical values that otherwise have a Y/N indicator

# In[3]:


data['Average_ACT_School'].fillna(data['Average_ACT_School'].mean(),inplace=True)
data['College_Enrollment_Rate_School'].fillna(data['College_Enrollment_Rate_School'].mean(),inplace=True)
data['Growth_ACT_Grade_11_Pct'].fillna(data['Growth_ACT_Grade_11_Pct'].mean(),inplace=True)
data['Attainment_ACT_Grade_11_Pct'].fillna(data['Attainment_ACT_Grade_11_Pct'].mean(),inplace=True)
data['Freshmen_On_Track_School_Pct_Year_2'].fillna(data['Freshmen_On_Track_School_Pct_Year_2'].mean(),inplace=True)
data['College_Persistence_School_Pct_Year_2'].fillna(data['College_Persistence_School_Pct_Year_2'].mean(),inplace=True)

data['Suspensions_Per_100_Students_Change'].fillna(0,inplace=True)
data['Misconducts_To_Suspensions_Change'].fillna(0,inplace=True)
data['Teacher_Attendance_Change'].fillna(0,inplace=True)
data['One_Year_Dropout_Rate_Change'].fillna(0,inplace=True)

data['Bilingual_Services'].fillna('U',inplace=True)
data['Refugee_Services'].fillna('U',inplace=True)


# Some values in the data set had counts of students in the school that were part of a group (low income, special ed, different ethnic groups, etc). We calculated rates for those groups using provided counts and student total count for the school. Then, dropped the original count columns.

# In[4]:


data['Student_Low_Income_Pct']=data['Student_Count_Low_Income']/data['Student_Count_Total']
data['Student_Special_Ed_Pct']=data['Student_Count_Special_Ed']/data['Student_Count_Total']
data['Student_English_Learners_Pct']=data['Student_Count_English_Learners']/data['Student_Count_Total']
data['Student_Black_Pct']=data['Student_Count_Black']/data['Student_Count_Total']
data['Student_Hispanic_Pct']=data['Student_Count_Hispanic']/data['Student_Count_Total']
data['Student_White_Pct']=data['Student_Count_White']/data['Student_Count_Total']
data['Student_Asian_Pct']=data['Student_Count_Asian']/data['Student_Count_Total']

data.drop(labels=['Student_Count_Low_Income','Student_Count_Special_Ed','Student_Count_English_Learners','Student_Count_Black','Student_Count_Hispanic','Student_Count_White','Student_Count_Asian'], axis=1,inplace=True)


# In the following step we are creating a new dataset with dummies for categorical variables

# In[5]:


data_dummies=pd.get_dummies(data)


# Next step is to create another dataset with all variables scaled from 0 to 1. This data set will be used for regression modeling.

# In[6]:


from sklearn.preprocessing import MinMaxScaler
min_max=MinMaxScaler()
min_max.fit(data_dummies)
data_scaled=pd.DataFrame(min_max.transform(data_dummies),index=data_dummies.index.values,columns=data_dummies.columns.values)

pd.set_option('display.max_columns', 100)
data_scaled.describe(include='all').T


# Checking description of all variables I can make sure that all variable have a count of 121, with min of 0 and max of 1.

# Last three steps export three datasets for use in analysis and modeling.

# In[7]:


data_dummies.to_csv('processed_data.csv')


# In[8]:


data.to_csv('processed_nodummies.csv')


# In[9]:


data_scaled.to_csv('processed_scaled.csv')

