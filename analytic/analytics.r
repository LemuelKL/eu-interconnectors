# Read data from data_day_ahead_prices.csv
dh_prices <- read.csv("data_day_ahead_prices.csv", header = TRUE)

# Set the first column name to date_time
colnames(dh_prices)[1] <- "date_time"

# Convert the date_time column to a date-time object
dh_prices$date_time <- as.POSIXct(dh_prices$date_time, format = "%Y-%m-%d %H:%M:%S")

# Create a new column with the day of the week
dh_prices$day_of_week <- weekdays(dh_prices$date_time, abbreviate = TRUE)
dh_prices$day_of_week <- factor(dh_prices$day_of_week, levels = c("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"))

# Create a new column with the hour of the day
dh_prices$hour_of_day <- format(dh_prices$date_time, "%H")

# Create a new column with the month of the year
dh_prices$month_of_year <- format(dh_prices$date_time, "%m")

# Create a new column with the year
dh_prices$year <- format(dh_prices$date_time, "%Y")

# Create a new column with the day of the month
dh_prices$day_of_month <- format(dh_prices$date_time, "%d")

# Create a new column with the week of the year
dh_prices$week_of_year <- format(dh_prices$date_time, "%U")

# Create a new column with the day of the year
dh_prices$day_of_year <- format(dh_prices$date_time, "%j")

# Create a new column with the season of the year
dh_prices$season <- ifelse(dh_prices$month_of_year %in% c("12", "01", "02"), "winter",
                           ifelse(dh_prices$month_of_year %in% c("03", "04", "05"), "spring",
                                  ifelse(dh_prices$month_of_year %in% c("06", "07", "08"), "summer",
                                         ifelse(dh_prices$month_of_year %in% c("09", "10", "11"), "autumn", NA))))

# Describe the data
summary(dh_prices)

library(ggplot2)

# Plot distribution and density of day ahead prices
ggplot(dh_prices, aes(x = price)) +
  geom_histogram(bins = 100, aes(y=..density..)) +
  geom_density(col = "green") +
  geom_vline(aes(xintercept = mean(price)), color = "red", linetype = "dashed", size = 0.1) +
  geom_vline(aes(xintercept = median(price)), color = "blue", linetype = "dashed", size = 0.1) +
  labs(x = "Day ahead price (€/MWh)", y = "Count", title = "Distribution of day ahead prices")

# Plot the day ahead prices by day of the week
ggplot(dh_prices, aes(x = day_of_week, y = price)) +
  geom_boxplot() +
  labs(x = "Day of the week", y = "Day ahead price (€/MWh)", title = "Day ahead prices by day of the week")

# Plot the day ahead prices by hour of the day
ggplot(dh_prices, aes(x = hour_of_day, y = price)) +
  geom_boxplot() +
  labs(x = "Hour of the day", y = "Day ahead price (€/MWh)", title = "Day ahead prices by hour of the day")

# Plot the day ahead prices by month of the year
ggplot(dh_prices, aes(x = month_of_year, y = price)) +
  geom_boxplot() +
  labs(x = "Month of the year", y = "Day ahead price (€/MWh)", title = "Day ahead prices by month of the year")

# Linear regression model
lm_price <- lm(price ~ hour_of_day, data = dh_prices)
lm_price

# Plot the residuals
plot(lm_price)

# Support vector machine model
library(e1071)
svm_price <- svm(price ~ hour_of_day, data = dh_prices)

# Plot the support vectors
plot(svm_price, dh_prices, hour_of_day ~ price)
