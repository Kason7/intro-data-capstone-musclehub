
# coding: utf-8

# # Capstone Project 1: MuscleHub AB Test

# ## Step 1: Get started with SQL

# Like most businesses, Janet keeps her data in a SQL database.  Normally, you'd download the data from her database to a csv file, and then load it into a Jupyter Notebook using Pandas.
# 
# For this project, you'll have to access SQL in a slightly different way.  You'll be using a special Codecademy library that lets you type SQL queries directly into this Jupyter notebook.  You'll have pass each SQL query as an argument to a function called `sql_query`.  Each query will return a Pandas DataFrame.  Here's an example:

# In[3]:


# This import only needs to happen once, at the beginning of the notebook
from codecademySQL import sql_query


# In[4]:


# Here's an example of a query that just displays some data
sql_query('''
SELECT *
FROM visits
LIMIT 5
''')


# In[ ]:


# Here's an example where we save the data to a DataFrame
df1 = sql_query('''
SELECT *
FROM applications
LIMIT 5
''')
print df1


# ## Step 2: Get your dataset

# Let's get started!
# 
# Janet of MuscleHub has a SQLite database, which contains several tables that will be helpful to you in this investigation:
# - `visits` contains information about potential gym customers who have visited MuscleHub
# - `fitness_tests` contains information about potential customers in "Group A", who were given a fitness test
# - `applications` contains information about any potential customers (both "Group A" and "Group B") who filled out an application.  Not everyone in `visits` will have filled out an application.
# - `purchases` contains information about customers who purchased a membership to MuscleHub.
# 
# Use the space below to examine each table.

# In[11]:


# Examine visits here
visits = sql_query('''
SELECT *
FROM visits
LIMIT 5
''')
visits_count = sql_query('''
SELECT COUNT(*)
FROM visits
LIMIT 5
''')
print visits
print visits_count


# In[7]:


# Examine fitness_tests here
fitness_tests = sql_query('''
SELECT *
FROM fitness_tests
LIMIT 5
''')
fitness_tests_count = sql_query('''
SELECT COUNT(*)
FROM fitness_tests
LIMIT 5
''')
print fitness_tests
print fitness_tests_count


# In[8]:


# Examine applications here
applications = sql_query('''
SELECT *
FROM applications
LIMIT 5
''')
applications_count = sql_query('''
SELECT COUNT(*)
FROM applications
LIMIT 5
''')
print applications
print applications_count


# In[9]:


# Examine purchases here
purchases = sql_query('''
SELECT *
FROM purchases
LIMIT 5
''')
purchases_count = sql_query('''
SELECT COUNT(*)
FROM purchases
LIMIT 5
''')
print purchases
print purchases_count


# In[12]:


# We'd like to download a giant DataFrame containing all of this data.  You'll need to write a query that does the following things:

1. Not all visits in  `visits` occurred during the A/B test.  You'll only want to pull data where `visit_date` is on or after `7-1-17`.

2. You'll want to perform a series of `LEFT JOIN` commands to combine the four tables that we care about.  You'll need to perform the joins on `first_name`, `last_name`, and `email`.  Pull the following columns:


- `visits.first_name`
- `visits.last_name`
- `visits.gender`
- `visits.email`
- `visits.visit_date`
- `fitness_tests.fitness_test_date`
- `applications.application_date`
- `purchases.purchase_date`

Save the result of this query to a variable called `df`.

get_ipython().set_next_input(u'Hint: your result should have 5004 rows.  Does it');get_ipython().magic(u'pinfo it')


# In[13]:


# 1. Not all visits in  visits occurred during the A/B test. You'll only want to pull data where visit_date is on or after 7-1-17.
visits_after_start = sql_query('''
SELECT *
FROM visits
WHERE visit_date > '7-01-17'
LIMIT 5
''')
visits_after_start_count = sql_query('''
SELECT COUNT(*)
FROM visits
WHERE visit_date > '7-01-17'
LIMIT 5
''')
print visits_after_start
print visits_after_start_count

# 2. You'll want to perform a series of LEFT JOIN commands to combine the four tables that we care about. You'll need to perform the joins on first_name, last_name, and email.
df = sql_query('''
SELECT visits.first_name, visits.last_name, visits.gender, visits.email, visits.visit_date, fitness_tests.fitness_test_date, applications.application_date, purchases.purchase_date
FROM visits 
LEFT JOIN fitness_tests
    ON visits.first_name = fitness_tests.first_name 
    AND visits.last_name = fitness_tests.last_name 
    AND visits.email = fitness_tests.email
LEFT JOIN applications
    ON visits.first_name = applications.first_name 
    AND visits.last_name = applications.last_name 
    AND visits.email = applications.email
LEFT JOIN purchases
    ON visits.first_name = purchases.first_name 
    AND visits.last_name = purchases.last_name 
    AND visits.email = purchases.email
WHERE visit_date > '7-01-17'
''')
print df


# ## Step 3: Investigate the A and B groups

# We have some data to work with! Import the following modules so that we can start doing analysis:
# - `import pandas as pd`
# - `from matplotlib import pyplot as plt`

# In[14]:


import pandas as pd
from matplotlib import pyplot as plt


# We're going to add some columns to `df` to help us with our analysis.
# 
# Start by adding a column called `ab_test_group`.  It should be `A` if `fitness_test_date` is not `None`, and `B` if `fitness_test_date` is `None`.

# In[15]:


ab_test_group_lambda = lambda row: 'A' if row.fitness_test_date > 0 else 'B'
df['ab_test_group'] = df.apply(ab_test_group_lambda, axis = 1)
print df


# Let's do a quick sanity check that Janet split her visitors such that about half are in A and half are in B.
# 
# Start by using `groupby` to count how many users are in each `ab_test_group`.  Save the results to `ab_counts`.

# In[16]:


ab_counts = df.groupby('ab_test_group').first_name.count()
print ab_counts


# We'll want to include this information in our presentation.  Let's create a pie cart using `plt.pie`.  Make sure to include:
# - Use `plt.axis('equal')` so that your pie chart looks nice
# - Add a legend labeling `A` and `B`
# - Use `autopct` to label the percentage of each group
# - Save your figure as `ab_test_pie_chart.png`

# In[17]:


ab_counts_names = ["A", "B"]
plt.pie(ab_counts, autopct='%0.1f%%')
plt.axis('equal')
plt.legend(ab_counts_names)
plt.savefig('ab_test_pie_chart.png')
plt.show()


# ## Step 4: Who picks up an application?

# Recall that the sign-up process for MuscleHub has several steps:
# 1. Take a fitness test with a personal trainer (only Group A)
# 2. Fill out an application for the gym
# 3. Send in their payment for their first month's membership
# 
# Let's examine how many people make it to Step 2, filling out an application.
# 
# Start by creating a new column in `df` called `is_application` which is `Application` if `application_date` is not `None` and `No Application`, otherwise.

# In[18]:


is_application_lambda = lambda row: 'Application' if row.application_date > 0 else 'No Application'
df['is_application'] = df.apply(is_application_lambda, axis = 1)
print df


# Now, using `groupby`, count how many people from Group A and Group B either do or don't pick up an application.  You'll want to group by `ab_test_group` and `is_application`.  Save this new DataFrame as `app_counts`

# In[19]:


app_counts = df.groupby('is_application').first_name.count()

print app_counts


# We're going to want to calculate the percent of people in each group who complete an application.  It's going to be much easier to do this if we pivot `app_counts` such that:
# - The `index` is `ab_test_group`
# - The `columns` are `is_application`
# Perform this pivot and save it to the variable `app_pivot`.  Remember to call `reset_index()` at the end of the pivot!

# In[60]:


app_counts = df.groupby(['ab_test_group', 'is_application']).first_name.count().reset_index()

app_pivot = app_counts.pivot(columns='is_application', index='ab_test_group', values='first_name').reset_index()

print app_pivot


# Define a new column called `Total`, which is the sum of `Application` and `No Application`.

# In[145]:


app_pivot_renamed = app_pivot.rename(columns={'Application': 'application', 'No Application': 'no_application'})

total_lambda = lambda row: row.application + row.no_application

app_pivot_renamed['Total'] = app_pivot_renamed.apply(total_lambda, axis = 1)

print app_pivot_renamed


# Calculate another column called `Percent with Application`, which is equal to `Application` divided by `Total`.

# In[146]:


percent_with_app = lambda row: (100 * (row.application) / (row.Total))

app_pivot_renamed['percent_with_application'] = app_pivot_renamed.apply(percent_with_app, axis = 1)

print app_pivot_renamed


# It looks like more people from Group B turned in an application.  Why might that be?
# 
# We need to know if this difference is statistically significant.
# 
# Choose a hypothesis tests, import it from `scipy` and perform it.  Be sure to note the p-value.
# Is this result significant?

# In[149]:


from scipy.stats import binom_test

pval = binom_test(325, n=2500, p=0.09)
print pval

# The result is a p-value of 0.00000000004, less than 0.05, which means the null hypothesis is rejected and it is certain that 
# there is a difference. The people in B group who did NOT do the fitness test, are more liekly to submit an application.


# ## Step 4: Who purchases a membership?

# Of those who picked up an application, how many purchased a membership?
# 
# Let's begin by adding a column to `df` called `is_member` which is `Member` if `purchase_date` is not `None`, and `Not Member` otherwise.

# In[150]:


is_member_lambda = lambda row: 'Member' if row.purchase_date > 0 else 'Not Member'
df['is_member'] = df.apply(is_member_lambda, axis = 1)
print df


# Now, let's create a DataFrame called `just_apps` the contains only people who picked up an application.

# In[151]:


just_apps = df[df.is_application == 'Application']
print just_apps


# Great! Now, let's do a `groupby` to find out how many people in `just_apps` are and aren't members from each group.  Follow the same process that we did in Step 4, including pivoting the data.  You should end up with a DataFrame that looks like this:
# 
# |is_member|ab_test_group|Member|Not Member|Total|Percent Purchase|
# |-|-|-|-|-|-|
# |0|A|?|?|?|?|
# |1|B|?|?|?|?|
# 
# Save your final DataFrame as `member_pivot`.

# In[154]:


member_group = just_apps.groupby(['is_member', 'ab_test_group']).first_name.count().reset_index()
member_pivot = member_group.pivot(columns='is_member', index='ab_test_group', values='first_name').reset_index()

member_pivot_renamed = member_pivot.rename(columns={'Member': 'member', 'Not Member': 'not_member'})
total_lambda2 = lambda row: row.member + row.not_member

member_pivot_renamed['total'] = member_pivot_renamed.apply(total_lambda2, axis = 1)


percent_purchase = lambda row: (100 * (row.member) / (row.total))
member_pivot_renamed['percent_purchase'] = member_pivot_renamed.apply(percent_purchase, axis = 1)

print member_pivot_renamed


# It looks like people who took the fitness test were more likely to purchase a membership **if** they picked up an application.  Why might that be?
# 
# Just like before, we need to know if this difference is statistically significant.  Choose a hypothesis tests, import it from `scipy` and perform it.  Be sure to note the p-value.
# Is this result significant?

# In[155]:


pval2 = binom_test(250, n=325, p=0.8)
print pval2

# The result is p-value 0.16 which is much higher than 0.05. That means there is no statistical significance in the variation.


# Previously, we looked at what percent of people **who picked up applications** purchased memberships.  What we really care about is what percentage of **all visitors** purchased memberships.  Return to `df` and do a `groupby` to find out how many people in `df` are and aren't members from each group.  Follow the same process that we did in Step 4, including pivoting the data.  You should end up with a DataFrame that looks like this:
# 
# |is_member|ab_test_group|Member|Not Member|Total|Percent Purchase|
# |-|-|-|-|-|-|
# |0|A|?|?|?|?|
# |1|B|?|?|?|?|
# 
# Save your final DataFrame as `final_member_pivot`.

# In[157]:


visitors_group = df.groupby(['is_member', 'ab_test_group']).first_name.count().reset_index()
visitor_pivot = visitors_group.pivot(columns='is_member', index='ab_test_group', values='first_name').reset_index()

visitor_pivot_renamed = visitor_pivot.rename(columns={'Member': 'member', 'Not Member': 'not_member'})
total_lambda3 = lambda row: row.member + row.not_member
visitor_pivot_renamed['total'] = visitor_pivot_renamed.apply(total_lambda3, axis = 1)

percent_purchase = lambda row: (100 * (row.member) / (row.total))
visitor_pivot_renamed['percent_purchase'] = visitor_pivot_renamed.apply(percent_purchase, axis = 1)

print visitor_pivot_renamed


# Previously, when we only considered people who had **already picked up an application**, we saw that there was no significant difference in membership between Group A and Group B.
# 
# Now, when we consider all people who **visit MuscleHub**, we see that there might be a significant different in memberships between Group A and Group B.  Perform a significance test and check.

# In[158]:


pval3 = binom_test(250, n=2500, p=0.07)
print pval3

# The result is p-value of 0.000000029, much less than 0.05 which means the null hypothesis is rejected and 
# there definately is a statistical difference.


# ## Step 5: Summarize the acquisition funel with a chart

# We'd like to make a bar chart for Janet that shows the difference between Group A (people who were given the fitness test) and Group B (people who were not given the fitness test) at each state of the process:
# - Percent of visitors who apply
# - Percent of applicants who purchase a membership
# - Percent of visitors who purchase a membership
# 
# Create one plot for **each** of the three sets of percentages that you calculated in `app_pivot`, `member_pivot` and `final_member_pivot`.  Each plot should:
# - Label the two bars as `Fitness Test` and `No Fitness Test`
# - Make sure that the y-axis ticks are expressed as percents (i.e., `5%`)
# - Have a title

# In[162]:


# Percent of visitors who applied
groups = ["Fitness Test", "No Fitness Test"]
percentage_app = [9, 13]

plt.bar(range(len(percentage_app)),percentage_app)

ax2 = plt.subplot()
ax2.set_xticks(range(len(groups)))
ax2.set_xticklabels(groups)
ax2.set_yticks([2, 4, 6, 8, 10, 12])
ax2.set_yticklabels(["2%", "4%", "6%", "8%", "10%", "12%"])
plt.title('Submitted Applications')
plt.savefig('submitted_applications.png')
plt.show()


# In[163]:


# Percent of applicants who purchased a membership
groups2 = ["Fitness Test", "No Fitness Test"]
percentage_app2 = [80, 76]

plt.bar(range(len(percentage_app2)),percentage_app2)

ax3 = plt.subplot()
ax3.set_xticks(range(len(groups2)))
ax3.set_xticklabels(groups2)
ax3.set_yticks([10, 20, 30, 40, 50, 60, 70, 80])
ax3.set_yticklabels(["10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%"])
plt.title('Applicants who Purchased')
plt.savefig('applicants_who_purchased.png')
plt.show()


# In[164]:


# Percent of visitors who purchased a membership
groups3 = ["Fitness Test", "No Fitness Test"]
percentage_app3 = [7, 10]

plt.bar(range(len(percentage_app3)),percentage_app3)

ax4 = plt.subplot()
ax4.set_xticks(range(len(groups3)))
ax4.set_xticklabels(groups3)
ax4.set_yticks([2, 4, 6, 8, 10])
ax4.set_yticklabels(["2%", "4%", "6%", "8%", "10%"])
plt.title('Visitors who Purchased')
plt.savefig('visitors_who_purchased.png')
plt.show()

