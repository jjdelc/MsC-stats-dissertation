install.packages("MASS")
install.packages("VGAM")
library(MASS)
library(VGAM)

set.seed(111)

# Load the data
enaho_sample <- read.csv('sample_data.csv')
enaho_sample$digital_poor <- as.ordered(enaho_sample$digital_poor)
enaho_sample$domain_fac <- factor(enaho_sample$domain)

# Split rows in training and testing data
train_indices <- sample(seq_len(nrow(enaho_sample)), size = 0.95 * nrow(enaho_sample))
train_set <- domain_data[train_indices, ]
test_set <- domain_data[-train_indices, ]

# Run the model
formula_c = "digital_poor ~ age_groups + domain + income_categories + educ_recode + gender"
model_c <- vglm(formula_c,
               	cumulative(link = 'logitlink', parallel = FALSE),
               	data = train_set)

aic_c <- AIC(model_c)
bic_c <- BIC(model_c)

summary(model_c)


#
# Predictions, Confusion Matrix
#
predicted_probs <- predict(model_c, newdata=test_set, type="response")
actual_categories <- test_set$digital_poor
confusion_matrix <- table(predicted_categories, actual_categories)
print(confusion_matrix)

#
# Evaluate the model per domain
#

split_by_domain <- split(enaho_sample, enaho_sample$domain_fac)
formula_c_domain = "digital_poor ~ age_groups + income_categories + educ_recode + gender"
models <- list()
predicted_categories_list <- list()
actual_categories_list <- list()
confusion_matrices <- list()
accuracies <- numeric(length(split_by_domain))
aic_values <- numeric(length(split_by_domain))

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

    # Calculate AIC
    aic_values[i] <- AIC(model)
}
# There were 45 warnings (use warnings() to see them)

# Print results for each domain
for (i in 1:length(split_by_domain)) {
    cat("\nDomain", i, ":\n")
    cat("Confusion Matrix:\n")
    print(confusion_matrices[[i]])
    cat("Accuracy:", accuracies[i], "\n")
    cat("AIC:", aic_values[i], "\n")
}
