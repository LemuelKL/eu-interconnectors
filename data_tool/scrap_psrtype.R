# Scrap html table that is immediately after the h3 element with id "_psrtype"
library(rvest)
url <- "https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html"
html <- read_html(url)
table <- html %>% html_nodes("h3#_psrtype ~ table") %>% html_table(header = TRUE)
table
write.csv(table, "psrtype.csv", row.names = FALSE, quote = FALSE)
