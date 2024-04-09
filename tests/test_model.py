import os
import sys

current_directory = os.getcwd()
sys.path.insert(0, current_directory)

from BWS.model import analysis
from BWS.database import db_interactions

# Adding attributes column
# db_interactions.insert_attributes('lyov',["ram","vam","sam","kam","lam","oam","pam","zam","pip","zip","lip"])

# Getting the specific survey
survey_design= analysis.get_survey_design('lyov')
print(survey_design.head())

# Pushing survey to the database with name "survet.lyov"
analysis.push_survey_design('lyov', survey_design)

# Question ?????????
#df = db_interactions.sql_to_pandas('SELECT * from survey.lyov')
#print(df.head())

