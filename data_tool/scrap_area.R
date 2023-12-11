# Scrap html table that is immediately after the h3 element with id "_psrtype"
library(rvest)
url <- "https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html"
html <- read_html(url)
table <- html %>% html_nodes("#content > div > div:nth-child(5) > div > div:nth-child(7) > div > div > div > div > div > div > div > div > div:nth-child(135) > div > div:nth-child(10) > table") %>% html_table(header = TRUE)
table
write.csv(table, "area_raw.csv", row.names = FALSE, quote = FALSE)
