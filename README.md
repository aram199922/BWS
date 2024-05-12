# BWS
Tool for conducting and analyzing best-worst scaling surveys
# The link of the package to pypi.org
https://pypi.org/project/myBWS/

# Setup Repository

Open new bash terminal (you need to have bash installed)
Follow the steps:
1. Create virtual environment:
$ python -m venv venv
2. Activate the virtual environment:
Windows: $ source ./venv/Scripts/activate
MacOS/Linux: $ venv/bin/activate
3. Install all packages and dependencies
$ pip install -r requirements.txt

Ready to use!!!

# Dealing with API

Do not forget to follow the steps which are described in the example.ipynb file.

1. Run run_business_owner_details.py
This will give an API link with which the business owner will be able to provide its company name, product name along with its attributes for which they want to conduct a survey (product development).
2. Run run_respondent.py
This will give an API link with which the users are going to complete the survey. 
3. Run run_business_owner_analysis.py
This will give an API link with which the business owner will be able to get the analysis conducted about their product.