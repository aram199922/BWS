import os
import sys
current_directory = os.getcwd()
sys.path.insert(0, current_directory)

from BWS.database import db_interactions
import pyreadr
import pandas as pd

# Number of survey blocks
nBl = 'number_of_blocks'
# Number of tasks a person will complete
nTs = 'number_of_tasks'
# Number of attributes a person will see in each task
nIt = 'number_of_items'
# Number of the overall attributes
nAttr = 'number_of_attributes'


def design_creation(attributes):
    """
    Return the json of the designed survey (by blocks).

    Parameters:
    Gets a list of attributes (minimum of 10 attributes).

    Returns:
    json: json file of the survey.
    """
    master_design = db_interactions.read_table('Master_Design')

    # Number of attributes.
    attribute_count = len(set(attributes))

    # Filtering master design accordingly
    design_0 = master_design[master_design[nAttr]==attribute_count]
    design = design_0[(design_0[nTs] == round(design_0[nTs].unique().mean())) &
                  (design_0[nIt] == round(design_0[nIt].unique().mean())) &
                 (design_0[nBl] == round(design_0[nBl].unique().mean()))]
    
    n_tasks = round(design_0[nTs].unique().mean())
    n_items = round(design_0[nIt].unique().mean())
    Balance_Mean = design['Balance_Mean'].min()

    design = design.drop(columns = [nBl,nIt,nTs,nAttr,'Critical_D','Balance_Mean'])
    design.dropna(axis=1,inplace=True)

    for column in design.columns:
        if 'item' in column:
            design[column] = design[column].astype(int)
    
    design[['Block', 'Task']] = design[['Block', 'Task']].astype(int)

    # Getting Final design and matching with our attributes
    final_design = design.reset_index(drop=True)
    item_columns = [col for col in final_design.columns if 'item' in col]
    for col in item_columns:
        final_design[col] = final_design[col].apply(lambda x: attributes[x - 1] if 1 <= x <= len(attributes) else x)
    
    # survey_design = {}
    # numbered_design = {}

    # design_params = {'Number of Attributes': attribute_count, 'Optimal number of tasks of the survey​': n_tasks, 'Optimal number of attributes per task of the survey​':n_items, 'Balanced Mean': Balance_Mean}
    # survey_design['Design_Params'] = [design_params]

    # numbered_design['Design_Params'] = [design_params]

    # grouped = design.groupby('Block')
    # for block, group in grouped:
    #     block_data = []
    #     for _, row in group.iterrows():
    #         row_dict = row.drop('Block').to_dict()
    #         block_data.append(row_dict)
    #     numbered_design[f"Block {block}"] = block_data
    # # Preparing for json
    # grouped = final_design.groupby('Block')
    # for block, group in grouped:
    #     block_data = []
    #     for _, row in group.iterrows():
    #         row_dict = row.drop('Block').to_dict()
    #         block_data.append(row_dict)
    #     survey_design[f"Block {block}"] = block_data
    return final_design

def output_1_simple_demographic(data):
    result_df = pd.DataFrame()
    non_demographic = ['Respondent_ID', 'Attribute', 'Block', 'Task', 'Response', 'Importance']
    
    simple_demographic_data = data.drop_duplicates(subset=['Respondent_ID'])
    
    for c in simple_demographic_data.columns:
        if c not in non_demographic and simple_demographic_data[c].dtype == 'object':
            group_counts = pd.DataFrame(simple_demographic_data.groupby(c)['Respondent_ID'].count())
            group_counts.reset_index(inplace=True)
            group_counts.rename(columns={c: 'Category', 'Respondent_ID': 'Count'}, inplace=True)
            group_counts['Demographic']=c
            result_df = pd.concat([result_df, group_counts], axis=0)
    
    return result_df

def ae_mln(data, prob = 0.95):
    """
    Calculate the analytical estimate for the MLN for a given dataframe.

    Parameters:
    data (pandas.DataFrame): The input dataframe.
    CI (float): Optional confidence interval (default = 0.95).

    Returns:
    pandas.DataFrame: Contains Total, Best, Worst, Neutral, b, se, lb, ub, choice_p.
    """
    # Calculate the degrees of freedom (sample Size - 1)
    df = data["Respondent_ID"].nunique() - 1

    # Aggregate data
    aggr_data = data.groupby('Attribute')['Response'].agg(['sum', 'count']).reset_index()

    # Count positive, negative, and neutral responses
    counts = data.groupby(['Attribute', 'Response']).size().unstack(fill_value=0)
    aggr_data['Best'] = counts[1].values
    aggr_data['Worst'] = counts[-1].values
    aggr_data['Neutral'] = counts[0].values

    # Calculate pj: (Nt + Np - Nn) / (2 * Nt)
    aggr_data['pj'] = (aggr_data['sum'] + aggr_data['count']) / (2 * aggr_data['count'])

    # Calculate bj = ln(pj / (1 - pj))
    aggr_data['b'] = np.log(aggr_data['pj'] / (1 - aggr_data['pj']))

    # Calculate the choice probabilities
    aggr_data['choice_p'] = np.exp(aggr_data['b']) / np.sum(np.exp(aggr_data['b']))

    # Calculate the standard error of bj: sqrt(1 / (pj * (1 - pj) * 2 * count))
    aggr_data['se'] = np.sqrt(1 / (aggr_data['pj'] * (1 - aggr_data['pj']) * 2 * aggr_data['count']))

    # Calculate the lower and upper bound for the given confidence level
    aggr_data['lb'] = aggr_data['b'] - t.ppf(1 - (1 - prob) / 2, df) * aggr_data['se']
    aggr_data['ub'] = aggr_data['b'] + t.ppf(1 - (1 - prob) / 2, df) * aggr_data['se']

    # Drop unnecessary columns
    aggr_data.drop(['sum', 'pj'], axis=1, inplace=True)

    # Rename columns
    aggr_data.rename(columns={'count': 'Total'}, inplace=True)

    return aggr_data

def output_2_general_importance_plot_df(data):
    """Return the json for the general importance plot
    
    Parameters:
    data (pandas.DataFrame): The input dataframe. 
    The data should be only for the General part (rather than the Company)
    
    Returns:
    json: The json data for the general importance plot
    """
    res1 = ae_mln(data)
    
    # if [lb, ub] is contained 0 then sig = "", if did not contain 0 then sig = "**"
    res1['sig'] = np.where((res1['lb'] <= 0) & (res1['ub'] >= 0), '', '**')
    # remove the following columns from res1
    res1.drop(['Total', 'Best', 'Worst', 'Neutral', 'se'], axis=1, inplace=True)
    # Change all column names
    res1.rename(columns={'b': 'General_Preference_of_Attributes',
                        'choice_p': 'General_Importance',
                        'lb': 'Lower_Bound',
                        'ub': 'Upper_Bound',
                        'sig': 'General_Significance'
                       }, inplace=True)
    
    return res1

def output_3_4_importance_by_demographic(data):
    static_columns = ['Respondent_ID', 'Attribute', 'Block', 'Task', 'Response', 'Importance']
    
    result_columns = ['Attribute','General_Importance','General_Significance','Demographic', 'Category']
    result = pd.DataFrame(columns=result_columns)
    for c in data.columns:
        if c not in static_columns and data[c].dtype == 'object':    
            unique_values_list = data[c].unique().tolist()
            for i in unique_values_list:
                data_subset = data[data[c] == i]
                res_subset = output_2_general_importance_plot_df(data_subset)
                for j in res_subset:
                    new_row = {'Attribute': j['Attribute'], 'General_Importance': j['General_Importance'],'General_Significance': j['General_Significance'],'Demographic': c,'Category' : i}
                    new_row_df = pd.DataFrame([new_row])
                    result = pd.concat([result, new_row_df], ignore_index=True)
    return result

