# -*- coding: utf-8 -*-
"""Tree Survival Prediction:

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1HhZznr2Mgoz-LyW9tXLRZJiuoDESrSaO
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

df =  pd.read_csv("/content/drive/MyDrive/Collab Dataset/Tree Survival Analysis/Tree_Data.csv")

df.sample(4)

df.columns

print(df['Species'].value_counts())

print(df['Soil'].value_counts())

print(df['Light_Cat'].value_counts())

print(df['Conspecific'].value_counts())

"""Data cleaning"""

df.describe(include='object')

"""Comment: All records missing EMF data are AMF Mycorrhizal type seedling species ('Myco' == 'AMF').
This indicates that EMF data was not measured for seedling species associated with arbuscular mycorrhizal fungi (AMF).
"""

# EMF: We will assume that AMF-associated seedlings do not have any EMF colonization.
# EMF: We will replace missing EMF values with 0 for AMF-associated seedlings.
# Alive: We will replace na with 'Not Alive' and 'X' with 'Alive'.
df['EMF'].fillna(0, inplace=True)
df['Alive'].fillna('Not Alive', inplace=True)
df['Alive'] = df['Alive'].replace('X', 'Alive')
df.isna().sum()

df['Event'] = df['Event'].dropna()

df.drop(columns=['Harvest','PlantDate','No', 'Plot','Subplot'], inplace=True)

df.head(2)

"""Handeling Catagorical Data"""

from sklearn.preprocessing import OrdinalEncoder

encoded_df = df.copy()

cat_cols_train = df.select_dtypes(include='object').columns

for col in cat_cols_train:
  oe = OrdinalEncoder()
  encoded_df[col] = oe.fit_transform(df[[col]])
  print(col)
  print(oe.categories)

encoded_df.sample(5)

df.describe()

palette = sns.color_palette('viridis')
def kdeplot_and_boxplot(df, columns):
    fig, ax = plt.subplots(4, 2, figsize = (30, 40))
    ax = ax.flatten()

    for i, col in enumerate(columns):
        sns.histplot(x = col, data=df, ax=ax[2 * i], color=palette[i], kde=True, lw=1.5, edgecolor='black')
        ax[2*i].set_title(col, fontweight = 'bold', fontfamily='serif', fontsize=20)
        sns.boxplot(x = col, data=df, ax=ax[2 * i+1], color=palette[i])
        ax[2 * i+1].set_title(col, fontweight = 'bold', fontfamily='serif', fontsize=20)

    plt.show()

num_columns = ['Phenolics', 'NSC', 'Lignin', 'Alive'] # Updated column names
kdeplot_and_boxplot(df,num_columns)

"""No Outliers detected exept NSC
Lets Handle it

"""

encoded_df.columns

#calculating IQR for treedbh
per_25= encoded_df['NSC'].quantile(0.25)
per_75= encoded_df['NSC'].quantile(0.75)
iqr= per_75-per_25

upper_limit = per_75 + 1.5*iqr
lower_limit = per_25 - 1.5*iqr

print(upper_limit)
print(lower_limit)

encoded_df = encoded_df[(encoded_df['NSC'] < upper_limit) & (encoded_df['NSC'] > lower_limit)]

encoded_df.shape

"""  **Creating a new DataFrame df_traits_AMF which includes traits and AMF.**"""

# Creating a new DataFrame df_traits_AMF which includes traits and AMF.
traits_AMF = ['Phenolics', 'NSC', 'Lignin', 'AMF']
df_traits_AMF = df[traits_AMF][df['Myco']=='AMF']

# Calculate correlation matrix
correlation_matrix = df_traits_AMF[['Phenolics', 'NSC', 'Lignin', 'AMF']].corr()

# Plot heatmap
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
plt.title('Correlation Heatmap')
plt.show()

"""Comment:
The correlation analysis provides insights into the relationships between AMF colonization and various traits of the seedlings:

Positive relationship with phenolics suggests a potential enhancement in defensive compounds.
Negligible relationship with NSC indicates little impact on carbohydrate storage.
Negative relationship with lignin suggests a possible trade-off between structural integrity and the benefits provided by AMF.

** Creating a new DataFrame df_traits_EMF which includes traits and EMF.**
"""

traits_EMF = ['Phenolics', 'NSC', 'Lignin', 'EMF']
df_traits_EMF = df[traits_EMF][df['Myco']=='EMF']

# Calculate correlation matrix
correlation_matrix = df_traits_EMF[['Phenolics', 'NSC', 'Lignin', 'EMF']].corr()

# Plot heatmap
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
plt.title('Correlation Heatmap')
plt.show()

"""Comment:
The correlation analysis provides insights into the relationships between EMF colonization and traits of the seedlings:

Weak to moderate positive relationship with phenolics suggests a potential minor enhancement in defensive compounds.
Negligible relationship with NSC indicates little impact on carbohydrate storage.
Negligible relationship with lignin indicates little impact on the structural integrity.
"""

X = encoded_df.drop('Event', axis=1)
y = encoded_df['Event']

X

y

# prompt: drop NaN value from the y

y = y.dropna()

from sklearn.model_selection import train_test_split

# Reset X and y to their original values before dropping NaN from y
X = encoded_df.drop('Event', axis=1)
y = encoded_df['Event']

# Drop rows with NaN values from both X and y
X = X[y.notna()]  # Keep rows in X where y is not NaN
y = y.dropna()   # Drop NaN values from y

# Now X and y should have the same number of samples
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=8)

print(X_train.shape)
print(X_test.shape)
print(y_train.shape)
print(y_test.shape)

"""**defining a function for Model Evaluation**"""

from sklearn.metrics import mean_squared_error, r2_score
def model_eval(actual, predicted):
  rmse = np.sqrt(mean_squared_error(actual, predicted))
  r2 = r2_score(actual, predicted)
  print('The RMSE value for the model is: ', round(rmse,3))
  print('The R2 Score for the model is: ', round(r2, 3))

"""# Linear Regression"""

from sklearn.linear_model import LinearRegression
lr = LinearRegression()
lr.fit(X_train, y_train)
lr_train = lr.predict(X_train)
lr_test = lr.predict(X_test)

model_eval(y_train, lr_train)

model_eval(y_test, lr_test)

"""# Logistic Regression"""

from sklearn.linear_model import LogisticRegression
lor = LogisticRegression()
lor.fit(X_train, y_train)
lor_train = lor.predict(X_train)
lor_test = lor.predict(X_test)

from sklearn.metrics import classification_report, confusion_matrix
y_pred = lor.predict(X_test)
print(classification_report(y_test, y_pred))

print(confusion_matrix(y_test, y_pred))

"""136 - true negatives
39 - false negatives
48 - false positives
194 - true positives

# Random Forest Regressor
"""

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

rf = RandomForestRegressor(n_estimators=100, random_state=42)
rf1= rf.fit(X_train, y_train)
cross_val_scores = cross_val_score(rf1, X, y, cv=5, scoring='r2')
print("Cross-validation R-squared scores:", cross_val_scores)
print("Mean R-squared score:", cross_val_scores.mean())

from sklearn.ensemble import AdaBoostRegressor
ada = AdaBoostRegressor()
ada.fit(X_train, y_train)
preds_ada_train = ada.predict(X_train)
preds_ada_test = ada.predict(X_test)

model_eval(y_train, preds_ada_train)
model_eval(y_test, preds_ada_test)

from sklearn.ensemble import GradientBoostingRegressor
gb = GradientBoostingRegressor()
gb.fit(X_train, y_train)
preds_gb_train = gb.predict(X_train)
preds_gb_test = gb.predict(X_test)

model_eval(y_train, preds_gb_train)
model_eval(y_test,preds_gb_test )

import xgboost as xg
xgb = xg.XGBRegressor()
xgb.fit(X_train, y_train)
preds_xgb_train = xgb.predict(X_train)
preds_xgb_test = xgb.predict(X_test)

model_eval(y_train, preds_xgb_train)
model_eval(y_test, preds_xgb_test)

"""TESTING"""

# We want to use a df in the same format as the data we submit to .predict()
columns = X_test.columns
print(columns)

encoded_df.sample(5)

# Assuming 'Species' was the first column you encoded in your loop:
species_categories = oe.categories_[0]  # Accessing the categories for the first encoded column

# Then, you can access the species category using an integer index:
print(f"The species encoded as 1 is: {species_categories[1]}")

test_df = pd.DataFrame([[1.0,1.0,0.0,2017,1,0.0,0.0,1.0,0.0,20,24,1.0,2.4,24,10,33,100,0.0]],
                       index=[0], columns=X.columns) # Use X.columns instead of X_test.columns

test_df.head()

df.sample(4)

xgb.predict(test_df)

