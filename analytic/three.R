# Read data
flows <- read.csv("data/physical_flow__NL_10YNL----------L_10Y1001A1001A65H_202111010000_202311010000.csv", header = TRUE)

# Rename first column to date_time
colnames(flows)[1] <- "date_time"

# Convert date_time to POSIXct
flows$date_time <- as.POSIXct(flows$date_time, format = "%Y-%m-%d %H:%M:%S")

flows

library(ggplot2)
# Plot data
ggplot(flows, aes(x = date_time, y = quantity)) + geom_line()

# Plot distribution of quantity
ggplot(flows, aes(x = quantity)) + geom_histogram(bins = 100)

# Describe quantity
summary(flows$quantity)

# Feature engineer temporal features
flows$month <- as.numeric(format(flows$date_time, "%m"))
flows$day <- as.numeric(format(flows$date_time, "%d"))
flows$hour <- as.numeric(format(flows$date_time, "%H"))
flows$day_of_week <- as.numeric(format(flows$date_time, "%u"))

# Add a column for moving average of last 3 points
flows$ma_3 <- zoo::rollmean(flows$quantity, 3, fill = NA)

# Remove rows with NA
flows <- flows[!is.na(flows$ma_3), ]

# Split data into train and test randomly
set.seed(123)
train <- flows[sample(nrow(flows), 0.8 * nrow(flows)), ]
test <- flows[setdiff(1:nrow(flows), rownames(train)), ]

# Print length of train and test
nrow(train)
nrow(test)

# Linear regression model with features: hour, day_of_week, month
model <- lm(quantity ~ hour + day_of_week + month, data = train)

# Print model summary
summary(model)

# predict on test set
test$quantity_pred <- predict(model, test)

# Plot predictions
ggplot(test, aes(x = date_time)) + 
  geom_line(aes(y = quantity, colour = "quantity")) +
  geom_line(aes(y = quantity_pred, colour = "quantity_pred")) +
  scale_colour_manual("", breaks = c("quantity", "quantity_pred"), values = c("black", "red"))


# Correlation analysis
cor(flows$quantity, flows$hour)
cor(flows$quantity, flows$day_of_week)
cor(flows$quantity, flows$month)
cor(flows$quantity, flows$ma_3)
