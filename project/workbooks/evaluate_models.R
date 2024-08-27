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


enaho_sample <- read.csv('/home/jj/enaho_sample.csv')


enaho_sample$digital_poor <- as.ordered(enaho_sample$digital_poor)
enaho_sample$domain_fac <- factor(enaho_sample$domain)

set.seed(333)

# Determine the number of rows in the dataset
total_rows <- nrow(enaho_sample)

# Create a random sample of row indices for the training set (95% of the rows)
train_indices <- sample(seq_len(total_rows), size = 0.95 * total_rows)

# Create the training and test datasets
train_set <- enaho_sample[train_indices, ]
test_set <- enaho_sample[-train_indices, ]

formula_a <- "digital_poor ~ age + domain + house_income + education + gender + electric_grid + illiterate"
formula_b <- "digital_poor ~ age_groups + domain + income_categories + educ_recode + gender + electric_grid + illiterate"
formula_c <- "digital_poor ~ age_groups + domain + income_categories + educ_recode + gender"
formula_d <- "digital_poor ~ age_groups + domain_fac + log_income + educ_recode + gender"
formula_e <- "digital_poor ~ age_groups + domain + log_income + educ_recode + gender"
formula_f <- "digital_poor ~ age_groups + domain + social_level + educ_recode + gender"

model_a = vglm(formula_a,
                cumulative(link = 'logitlink', parallel = FALSE),
                data = train_set)
model_b = vglm(formula_b,
                cumulative(link = 'logitlink', parallel = FALSE),
                data = train_set)
model_c = vglm(formula_c,
                cumulative(link = 'logitlink', parallel = FALSE),
                data = train_set)
model_d = vglm(formula_d,
                cumulative(link = 'logitlink', parallel = FALSE),
                data = train_set)
model_e = vglm(formula_e,
                cumulative(link = 'logitlink', parallel = FALSE),
                data = train_set)
model_f = vglm(formula_f,
                cumulative(link = 'logitlink', parallel = FALSE),
                data = train_set)


predicted_probs <- predict(model_c, newdata = test_set, type = "response")

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

fitted_probs <- fitted(model_c)
residuals1 <- (observed_bin1 - fitted_probs[,1])
residuals2 <- (observed_bin2 - fitted_probs[,2])
residuals3 <- (observed_bin3 - fitted_probs[,3])
hist(residuals1, 100)
hist(residuals2, 100)
hist(residuals3, 100)
