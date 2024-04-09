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

