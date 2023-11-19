# Read data
flows <- read.csv("data_physical_flows__NL_10YNL----------L_10Y1001A1001A82H_202301010000_202302010000.csv", header = TRUE)

# Rename first column to date_time
colnames(flows)[1] <- "date_time"

# Convert date_time to POSIXct
flows$date_time <- as.POSIXct(flows$date_time, format = "%Y-%m-%d %H:%M:%S")

flows

library(ggplot2)
# Plot data
ggplot(flows, aes(x = date_time, y = quantity)) + geom_line()

# Compute and plot moving average of last 10 points
flows$ma_90 <- zoo::rollmean(flows$quantity, 90, fill = NA)
flows$ma_60 <- zoo::rollmean(flows$quantity, 60, fill = NA)
flows$ma_30 <- zoo::rollmean(flows$quantity, 30, fill = NA)

# Plot the 3 moving averages
ggplot(flows, aes(x = date_time)) + 
  geom_line(aes(y = quantity, colour = "quantity")) +
  geom_line(aes(y = ma_90, colour = "ma_90")) +
  geom_line(aes(y = ma_60, colour = "ma_60")) +
  geom_line(aes(y = ma_30, colour = "ma_30")) +
  scale_colour_manual("", breaks = c("quantity", "ma_90", "ma_60", "ma_30"), values = c("black", "red", "blue", "green"))
