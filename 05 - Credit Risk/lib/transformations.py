# -*- coding: utf-8 -*-
"""
Created on Sat Jun  2 10:33:42 2018

@author: vasil
"""

def transform_bureau_data(index):
    '''
    Generates the following features for each applicant:
    
    Input:
    df - bureau dataset
    index - applicants on which we want to subset the bureau dataset (trainig, validation, testing)
    
    Output: 
    dataframe with all new features and index 'SK_ID_CURR'
    
    CNT_ACTIVE_LOANS  - number of active loans with other institutions
    CNT_BAD_LOANS     - number of bad loans with other institutions
    CNT_CLOSED_LOANS  - number of closed loans with other institutions
    CNT_SOLD_LOANS    - number of loans sold by the other institutions
    
    AMT_ACTIVE_LOANS  - total outstanding loans amount with other istitutions
    AMT_BAD_LOANS     - total bad loans amount with other institutions
    AMT_CLOSED_LOANS  - total amount of closed loans with other institutions
    AMT_SOLD_LOANS    - total amount of sold loans with other institutions
    
    DAYS_OUTSTANDING  - days due of the loan which ends last
    DAYS_RECENT_CLOSE - days since the applicant closed his most recent loan
    
    AMT_OUTSTD_0_YEAR - outstanding amount due less than a year
    AMT_OUTSTD_1_YEAR - outstanding amount due within [1, 2) years
    AMT_OUTSTD_2_YEAR - outstanding amount due within [2, 3) years
    AMT_OUTSTD_3_YEAR - outstanding amount due within [3, 4) years
    AMT_OUTSTD_4_YEAR - outstanding amount due within [4, 5) years
    AMT_OUTSTD_5_YEAR - outstanding amount due within [5, inf) years
    
    CNT_PROLONGED     - total number of prolongations for active credits
    '''
    def column_labels_bureau():
        '''
        Creates nested dictionaries used for renaming the dfs' column names
        '''
        labels = {}

        labels['num_credits'] = {
              'Active'   : 'CNT_ACTIVE_LOANS',
              'Bad debt' : 'CNT_BAD_LOANS',
              'Closed'   : 'CNT_CLOSED_LOANS',
              'Sold'     : 'CNT_SOLD_LOANS'
             }

        labels['amt_credits'] = {
              'Active'   : 'AMT_ACTIVE_LOANS',
              'Bad debt' : 'AMT_BAD_LOANS',
              'Closed'   : 'AMT_CLOSED_LOANS',
              'Sold'     : 'AMT_SOLD_LOANS'
             }

        labels['max_days_active'] = {
              'Active'   : 'DAYS_OUTSTANDING',
              'Bad debt' : 'DROP_1',
              'Closed'   : 'DROP_2',
              'Sold'     : 'DROP_3'
             }

        labels['max_days_closed'] = {
              'Active'   : 'DROP_4',
              'Bad debt' : 'DROP_5',
              'Closed'   : 'DAYS_RECENT_CLOSE',
              'Sold'     : 'DROP_6'
             }

        labels['cnt_prolonged'] = {
              'Active'   : 'CNT_PROLONGED',
              'Bad debt' : 'DROP_7',
              'Closed'   : 'DROP_8',
              'Sold'     : 'DROP_9'
             }

        return labels
    
    df = pd.read_csv('../input/bureau.csv.zip', compression='infer')
    
    # taking a subset of the bureau dataset
    df = df.loc[index,:]
    
    num_credits = pd.DataFrame(
        df.pivot_table(
            index='SK_ID_CURR', 
            columns='CREDIT_ACTIVE', 
            values='SK_ID_BUREAU', 
            aggfunc='count', 
            fill_value=0
        ).to_records()
    )
    
    amt_credits = pd.DataFrame(
        df.pivot_table(
            index='SK_ID_CURR', 
            columns='CREDIT_ACTIVE', 
            values='AMT_CREDIT_SUM_DEBT', 
            aggfunc='sum', 
            fill_value=0
        ).to_records()
    )
    
    max_days_active = pd.DataFrame(
        df.pivot_table(
            index='SK_ID_CURR', 
            columns='CREDIT_ACTIVE', 
            values='DAYS_CREDIT_ENDDATE', 
            aggfunc='max', 
            fill_value=0
        ).to_records()
    )
    
    max_days_closed = pd.DataFrame(
        df.pivot_table(
            index='SK_ID_CURR', 
            columns='CREDIT_ACTIVE', 
            values='DAYS_ENDDATE_FACT', 
            aggfunc='max', 
            fill_value=0
        ).to_records()
    )
    
    cnt_prolonged = pd.DataFrame(
        df.pivot_table(
            index='SK_ID_CURR', 
            columns='CREDIT_ACTIVE', 
            values='CNT_CREDIT_PROLONG', 
            aggfunc='sum',
            fill_value=0
        ).to_records()
    )
    
    # credit amounts due for the next 5+ years
    df.loc[:,'YEARS_ENDDATE'] = df.loc[:,'DAYS_CREDIT_ENDDATE']//365
    df['YEARS_ENDDATE'].fillna(0,inplace=True)
    df['YEARS_ENDDATE'].clip(lower=0, upper=5,inplace=True)
    
    amt_credits_by_year = pd.DataFrame(
        df.pivot_table(
            index='SK_ID_CURR', 
            columns=['CREDIT_ACTIVE','YEARS_ENDDATE'], 
            values='AMT_CREDIT_SUM_DEBT', 
            aggfunc='sum', 
            fill_value=0
        ).to_records()
    )
    amt_credits_by_year.set_index('SK_ID_CURR', inplace=True)
    columns = amt_credits_by_year.columns[:6]
    amt_credits_by_year = amt_credits_by_year[columns] # take only the first 6 columns the rest is garbage
    del columns  
    
    # number of credits in the past year
    df.loc[:,'YEARS_OPEN_DATE'] = df.loc[:,'DAYS_CREDIT']//365
    df['YEARS_OPEN_DATE'].fillna(0,inplace=True)
    df['YEARS_OPEN_DATE'].clip(lower=-5, upper=0,inplace=True)
    
    num_active_credits_past_years = pd.DataFrame(
        df.pivot_table(
            index='SK_ID_CURR', 
            columns=['CREDIT_ACTIVE','YEARS_OPEN_DATE'], 
            values='SK_ID_BUREAU', 
            aggfunc='count', 
            fill_value=0
        ).to_records()
    )
    num_active_credits_past_years.set_index('SK_ID_CURR', inplace=True)
    columns = num_active_credits_past_years.columns[:6]
    num_active_credits_past_years = num_active_credits_past_years[columns] # take only the first 6 columns the rest is garbage
    del columns  
    
    num_credits.set_index('SK_ID_CURR', inplace=True)
    amt_credits.set_index('SK_ID_CURR', inplace=True)
    max_days_active.set_index('SK_ID_CURR', inplace=True)
    max_days_closed.set_index('SK_ID_CURR', inplace=True)
    cnt_prolonged.set_index('SK_ID_CURR', inplace=True)

    labels = column_labels_bureau()
    
    num_credits.rename(columns=labels['num_credits'], inplace=True)
    amt_credits.rename(columns=labels['amt_credits'], inplace=True)
    max_days_active.rename(columns=labels['max_days_active'], inplace=True)
    max_days_closed.rename(columns=labels['max_days_closed'], inplace=True)
    cnt_prolonged.rename(columns=labels['cnt_prolonged'], inplace=True)
        
    amt_credits_by_year.columns = [
        'AMT_OUTSTD_0_YEAR', 
        'AMT_OUTSTD_1_YEAR', 
        'AMT_OUTSTD_2_YEAR', 
        'AMT_OUTSTD_3_YEAR',
        'AMT_OUTSTD_4_YEAR',
        'AMT_OUTSTD_5_YEAR'
    ]
    
    num_active_credits_past_years.columns = [
        'CNT_ACT_LOANS_OPEN_5_YEAR',
        'CNT_ACT_LOANS_OPEN_4_YEAR',
        'CNT_ACT_LOANS_OPEN_3_YEAR',
        'CNT_ACT_LOANS_OPEN_2_YEAR',
        'CNT_ACT_LOANS_OPEN_1_YEAR',
        'CNT_ACT_LOANS_OPEN_0_YEAR',
    ]
    
    transformed = pd.DataFrame(index=num_credits.index)
    
    transformed = transformed.join(
        [
            num_credits,
            amt_credits,
            max_days_active,
            max_days_closed,
            amt_credits_by_year,
            cnt_prolonged,
            num_active_credits_past_years
        ]
    )

    columns_to_drop = []
    
    for column in transformed:
        words = column.split('_')
        if words[0] == 'DROP':
            columns_to_drop.append(column)
            
    transformed.drop(columns_to_drop, inplace=True, axis=1)
    
    del df
    
    return transformed