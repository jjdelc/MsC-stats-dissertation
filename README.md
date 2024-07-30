# MsC-stats-dissertation

Files to download and process data for MsC Applied Statistics dissertation.

This repo allows to download the ENAHO[1] survey data from:

> https://proyectos.inei.gob.pe/microdatos/Consulta_por_Encuesta.asp


This uses Jupyter Notebook:

```
python3.10 -m venv venv 
. ./venv/bin/activate
pip install -U pip
pip install jupyter
pip install pandas
pip install matplotlib
pip install seaborn
pip install pyreadstat
pip install savReaderWriter
pip install statsmodels
pip install scikit-learn

```

Sample usage to verify that data has loaded correctly:
```
from survey import SurveyReader
from reporter import Reporter
survey = SurveyReader("../ENAHO/")
survey.read_files()
reporter = Reporter(survey)
yearly_modules = reporter.yearly_modules()
yearly_cols = reporter.modules_dims("cols")
yearly_rows = reporter.modules_dims("rows")
```

Ensure that all years have files for all modules
Check that all surveys' .sav filename is reasonable
Check rows and columns for all surveys that they are within similar size
Check all the questions made yearly for a module
Check all the common questions for a module in all years
Report of all questions labels
Filtering .sav files per module
Reading data dictionary
Translating questions using Google Docs translate feature (Via CSV, spreadsheet)
Modules that need special treatment bc files are split


Statsmodel
https://www.statsmodels.org/stable/gettingstarted.html
For linear regressions

ENAHO papers
https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q=Peru+ENAHO&btnG=
Computing poverty in ENAHO
https://www.youtube.com/watch?v=LkWgRqG2y-w
Joining modules
https://www.youtube.com/watch?v=SW0wHxO78S4

Canasta básica
https://m.inei.gob.pe/prensa/noticias/pobreza-monetaria-afecto-al-290-de-la-poblacion-el-ano-2023-15137/
https://www.inei.gob.pe/media/MenuRecursivo/publicaciones_digitales/Est/Lib1728/Libro39.pdf
https://cdn.www.gob.pe/uploads/document/file/6324788/5558423-peru-evolucion-de-la-pobreza-monetaria-2014-2023.pdf

Secondary ethics review
https://app.onlinesurveys.jisc.ac.uk/s/bbk/ethics-form-23-24-secondary-data-analysis?resume=clxnochbd0001da968qbi3wk2&resume-token=puoAW5FH5A

Ordinal regression
https://www.youtube.com/watch?v=ZchGek2JRVQ
https://www.youtube.com/watch?v=jWIJ7P1G9P4
https://www.youtube.com/watch?v=G39fjSdkeyA


## Caveats

### Incompatible libraries

Library savReaderWriter is not compatible with python 3.10
So it needs a bit of manual adjusting to change an import
for `collections.Iterator` to `collections.abc.Iterator`.

### Interrupted downloads

Sometimes, the downloads get aborted from the server, so when
it seems that it all finished, turns out some files are missing.

Using the Reporter class helps to identify the missing entries and
re-download manually.


### Inconsistency in file structure:

Year 2015 needs manual unzipping because most of the module
files are not inside a directory.

Something along these lines is needed:

```
for zip_file in *.zip; do
    base_name="${zip_file%%.*}" # Extract filename without extension

    # Create a directory with the filename if it doesn't exist
    if [ ! -d "$base_name" ]; then
        mkdir "$base_name"
    fi

    # Unzip the files into the directory or directly into the current directory
    unzip -d "$base_name" "$zip_file" || unzip "$zip_file"

    # Remove the zip file
    #rm "$zip_file"
done
```

And then manually fix a few folders manually.



[1] ENAHO - Encuesta Nacional de Hogares



# Literacy review

Poverty, Household Structure and Consumption of Foods Away from Home in Peru in 2019: A Cross-Sectional Study 
https://www.mdpi.com/2304-8158/11/17/2547


Households with and without the presence of adolescents, probability of expenditure on food consumed away from home, according to
ENAHO 2021: a cross-sectional study [version 1; peer review: 1 not approved] 
https://f1000research.com/articles/12-1296

Inequalities in access to safe drinking water in Peruvian households according to city size: an analysis from 2008 to 2018
https://link.springer.com/article/10.1186/s12939-021-01466-7

Measuring Out-of-pocket Payment, Catastrophic Health Expenditure and the Related Socioeconomic Inequality in Peru: A Comparison Between 2008 and 2017
https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7411247/


R Code:
------------------------

```R
install.packages("MASS")
install.packages("brant")
install.packages("VGAM")
install.packages("erer")  # Requires curl dev headers # sudo apt-get install libcurl4-openssl-dev   
install.packages("margins")

library(MASS)
# For the brant test
library(brant)
# For the generalized ordered logit
library(VGAM)
# For marginal effects
#library(erer)
library(margins)

# Data on marital happiness and affairs
# Documentation: https://vincentarelbundock.github.io/Rdatasets/doc/Ecdat/Fair.html
mar <- read.csv('/home/jj/Out_87.csv')

> na_positions <- is.na(mar_factors_df)
> 
> # Summary of NA values in each column
> colSums(na_positions)
mar_factors <- lapply(mar, factor)
mar_factors_df <- data.frame(mar_factors)
mar_factors_df$digital_poor <- as.ordered(mar_factors_df$digital_poor)

# See how various factors predict marital happiness
m <- polr(factor(digital_poor) ~ age + log_income + region + education + electric_grid,
          data = mar, 
          method = 'logistic' # change to 'probit' for ordered probit
          )

summary(m)

# Brant test of proportional odds
brant(m)
# The "Omnibus" probability is .03, if we have alpha = .05 then we reject proportional odds
# Specifically the test tells us that education is the problem. Dang.

# We can use vglm for the generalized ordered logit
gologit <- vglm(factor(digital_poor) ~ age + log_income + region + education + electric_grid,
                cumulative(link = 'logitlink', parallel = FALSE), # parallel = FALSE tells it not to assume parallel lines
                data = mar)
                
summary(gologit)

marginal_effects_gologit <- margins(gologit)

# Display the marginal effects
print(marginal_effects_gologit)

# Summary of marginal effects
summary(marginal_effects_gologit)

gologit2 <- vglm(digital_poor ~ income_categories + age_groups + educ_recode,
                 cumulative(link = "logitlink", parallel = FALSE), 
                 data = mar)

# Calculate AIC and BIC for both models
aic_first_model <- AIC(gologit)
bic_first_model <- BIC(gologit)

aic_second_model <- AIC(gologit2)
bic_second_model <- BIC(gologit2)

# Print AIC and BIC values for comparison
print(paste("AIC (first model):", aic_first_model))
print(paste("BIC (first model):", bic_first_model))

print(paste("AIC (second model):", aic_second_model))
print(paste("BIC (second model):", bic_second_model))

```

```R

# This model seems to do it
enaho_sample <- read.csv('/home/jj/enaho_sample.csv')

columns_to_convert <- c(
  "rural",
  "gender",
  "electric_grid",
  "social_level",
  "domain",
  "digital_poor",
  "region",
  "educ_recode",
  "illiterate",
  "income_categories",
  "age_groups",
  "poor"
)

# Loop through each column name and convert it to a factor
for (col in columns_to_convert) {
  enaho_sample[[col]] <- factor(enaho_sample[[col]])
}
enaho_sample$digital_poor <- as.ordered(enaho_sample$digital_poor)
enaho_sample$domain_fac <- factor(enaho_sample$domain)



# Determine the number of rows in the dataset
total_rows <- nrow(enaho_sample)

# Create a random sample of row indices for the training set (95% of the rows)
train_indices <- sample(seq_len(total_rows), size = 0.95 * total_rows)

# Create the training and test datasets
train_set <- enaho_sample[train_indices, ]
test_set <- enaho_sample[-train_indices, ]

good_formula <- "digital_poor ~ age_groups + domain + social_level + educ_recode + gender"
formula <- "digital_poor ~ age + domain + house_income + education + gender + electric_grid + illiterate"
gologit <- vglm(formula,
                 cumulative(link = 'logitlink', parallel = FALSE),
                 data = train_set)
parallel <- vglm(digital_poor ~ age_groups + domain + social_level + educ_recode + gender,
                 cumulative(link = 'logitlink', parallel = TRUE),
                 data = train_set)

AIC(gologit)
BIC(gologit)
AIC(parallel)
BIC(parallel)

#vglm(formula = digital_poor ~ age_groups + REGION + social_level + 
#    education + gender, family = cumulative(link = "logitlink", 
#    parallel = FALSE), data = mar)

predicted_probs <- predict(gologit, newdata = test_set, type = "response")

# Convert predicted probabilities to predicted categories
# Assuming your response variable has 4 levels
predicted_categories <- apply(predicted_probs, 1, function(row) which.max(row))

# Compare predicted values to actual values
actual_categories <- test_set$digital_poor

# Create a confusion matrix to evaluate the predictions
confusion_matrix <- table(predicted_categories, actual_categories)

# Print the confusion matrix
print(confusion_matrix)

# Calculate accuracy
accuracy <- sum(predicted_categories == actual_categories) / length(actual_categories)
cat("Accuracy: ", accuracy, "\n")

enaho_sample$domain_fac = factor(enaho_sample$domain)
split_by_domain <- split(enaho_sample, enaho_sample$domain_fac)
models <- list()
predicted_categories_list <- list()
actual_categories_list <- list()
confusion_matrices <- list()
accuracies <- numeric(length(split_by_domain))

# Loop through each domain subset
for (i in 1:length(split_by_domain)) {
  # Get the current subset
  domain_data <- split_by_domain[[i]]
  
  # Split into training and testing sets
  train_indices <- sample(seq_len(nrow(domain_data)), size = 0.95 * nrow(domain_data))
  train_set <- domain_data[train_indices, ]
  test_set <- domain_data[-train_indices, ]
  
  # Fit the model
  model <- vglm(formula_c_domain,
                cumulative(link = 'logitlink', parallel = FALSE),
                data = train_set)
  
  # Store the model
  models[[i]] <- model
  
  # Predict on the test set
  predicted_probs <- predict(model, newdata = test_set, type = "response")
  predicted_categories <- apply(predicted_probs, 1, function(row) which.max(row))
  actual_categories <- test_set$digital_poor
  
  # Store predictions and actual categories
  predicted_categories_list[[i]] <- predicted_categories
  actual_categories_list[[i]] <- actual_categories
  
  # Create confusion matrix
  confusion_matrix <- table(predicted_categories, actual_categories)
  confusion_matrices[[i]] <- confusion_matrix
  
  # Calculate accuracy
  accuracy <- sum(predicted_categories == actual_categories) / length(actual_categories)
  accuracies[i] <- accuracy
}

# Print results for each domain
for (i in 1:length(split_by_domain)) {
  cat("\nDomain", i, ":\n")
  cat("Confusion Matrix:\n")
  print(confusion_matrices[[i]])
  cat("Accuracy:", accuracies[i], "\n")
}

```

```output
> summary(gologit)

Call:
vglm(formula = factor(digital_poor) ~ age + log_income + region + 
    education + electric_grid, family = cumulative(link = "logitlink", 
    parallel = FALSE), data = mar)

Coefficients: 
                  Estimate Std. Error    z value Pr(>|z|)    
(Intercept):1    6.675e+00  3.614e-01  1.847e+01  < 2e-16 ***
(Intercept):2    1.305e+01  5.654e-05  2.308e+05  < 2e-16 ***
(Intercept):3    1.302e+01  5.607e-05  2.323e+05  < 2e-16 ***
age:1            2.625e-02  1.599e-03  1.642e+01  < 2e-16 ***
age:2            2.975e-02  1.693e-07  1.757e+05  < 2e-16 ***
age:3            2.952e-02  1.688e-07  1.748e+05  < 2e-16 ***
log_income:1    -2.035e+00  7.718e-02 -2.636e+01  < 2e-16 ***
log_income:2    -2.044e+00  1.044e-05 -1.957e+05  < 2e-16 ***
log_income:3    -2.042e+00  1.038e-05 -1.967e+05  < 2e-16 ***
region:1         1.214e-01  1.721e-02  7.057e+00 1.70e-12 ***
region:2        -1.779e-01  8.411e-06 -2.115e+04  < 2e-16 ***
region:3        -1.708e-01  8.406e-06 -2.032e+04  < 2e-16 ***
education:1     -1.133e-01  2.506e-02 -4.521e+00 6.15e-06 ***
education:2     -2.020e-01  9.108e-07 -2.218e+05  < 2e-16 ***
education:3     -2.029e-01  9.071e-07 -2.236e+05  < 2e-16 ***
electric_grid:1 -1.808e+00  6.205e-02 -2.913e+01  < 2e-16 ***
electric_grid:2 -6.704e-01  1.163e-05 -5.766e+04  < 2e-16 ***
electric_grid:3 -6.594e-01  1.150e-05 -5.735e+04  < 2e-16 ***
---
Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1

Names of linear predictors: logitlink(P[Y<=1]), logitlink(P[Y<=2]), logitlink(P[Y<=3])

Residual deviance: 10926.47 on 41730 degrees of freedom

Log-likelihood: NA on 41730 degrees of freedom

Number of Fisher scoring iterations: 2 

Warning: Hauck-Donner effect detected in the following estimate(s):
'(Intercept):3', 'age:3', 'log_income:1', 'log_income:2', 'region:2', 'education:2', 'electric_grid:2'


Exponentiated coefficients:
          age:1           age:2           age:3    log_income:1    log_income:2    log_income:3        region:1        region:2        region:3 
      1.0266012       1.0301994       1.0299582       0.1307297       0.1295351       0.1298291       1.1291026       0.8370404       0.8430044 
    education:1     education:2     education:3 electric_grid:1 electric_grid:2 electric_grid:3 
      0.8928655       0.8170800       0.8163782       0.1640411       0.5115284       0.5171605 
Warning message:
```

logit(P(Y <= 1)) = 6.675 + 0.02625 * age - 2.035 * log(income) + 0.1214 * region - 0.1133 * education - 1.808 * electric_grid
logit(P(Y <= 2)) = 13.05 + 0.02975 * age - 2.044 * log(income) - 0.1779 * region - 0.202 * education - 0.6704 * electric_grid
logit(P(Y <= 3)) = 13.02 + 0.02952 * age - 2.042 * log(income) - 0.1708 * region - 0.2029 * education - 0.6594 * electric_grid

logit(P) = ln(P / (1 - P))

