# Read data
flows <- read.csv("data/physical_flow__NL_10YNL----------L_10Y1001A1001A65H_202304010000_202311010000.csv", header = TRUE)
prices <- read.csv("data/day_ahead_price__10YNL----------L_202304010000_202311010000.csv", header = TRUE)
generations <- read.csv("data/actual_generation_per_production_type__10YNL----------L_202304010000_202311010000.csv", header = TRUE)


# Rename first column to date_time
colnames(flows)[1] <- "date_time"
colnames(prices)[1] <- "date_time"
colnames(generations)[1] <- "date_time"

# Convert date_time to POSIXct
flows$date_time <- as.POSIXct(flows$date_time, format = "%Y-%m-%d %H:%M:%S")
prices$date_time <- as.POSIXct(prices$date_time, format = "%Y-%m-%d %H:%M:%S")
generations$date_time <- as.POSIXct(generations$date_time, format = "%Y-%m-%d %H:%M:%S")

flows
prices

# Sum all the generations for each date_time
generations$total <- rowSums(generations[, 2:ncol(generations)])
generations

# Merge three data frames by date_time
df <- merge(flows, prices, by = "date_time")
df <- merge(df, generations, by = "date_time")
df

# Count NA values
colSums(is.na(df))

# Linear regression model to predict quantity using all other variables except date_time
model <- lm(quantity ~ . - date_time, data = df)
summary(model)

# Split data into training and test sets randomly
set.seed(123)
train <- sample(nrow(df), 0.8 * nrow(df))
train_df <- df[train, ]
test_df <- df[-train, ]

# SVM model to predict quantity using all other variables except date_time
library(e1071)
model <- svm(quantity ~ . - date_time, data = train_df, kernel = "radial", cost = 1000, gamma = 10, epsilon = 0.1)
summary(model)

# Build many SVM models with different parameters and pick the best one
library(caret)
tune.out <- tune.svm(quantity ~ . - date_time, data = train_df, kernel = "radial", cost = 10^(-1:2), gamma = c(0.5, 1, 2, 3, 4, 5))
summary(tune.out)

# Predict quantity using test set
pred <- predict(model, test_df)
pred

# Calculate RMSE
rmse <- sqrt(mean((test_df$quantity - pred)^2))
rmse

# Plot actual vs predicted
library(ggplot2)
ggplot(data = test_df, aes(x = date_time, y = quantity)) + geom_line() + geom_line(aes(y = pred), color = "red")

# Plot flow vs total
ggplot(data = df, aes(x = total, y = quantity)) + geom_point()

