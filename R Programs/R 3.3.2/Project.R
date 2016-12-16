library(dplyr)
library(lubridate)

#Read read_output file and prepare it for Tableau visualizations


#Read File into the system
final_tags <- read.csv("~/PycharmProjects/F16/Data Mining/Project/final_tags.csv", header=TRUE)

#Convert time to a string
final_tags$time = sapply(final_tags$time, as.character)

#Create separate columns for each part of time
final_tags$Weekday = strsplit(final_tags$time, "\\s+")
final_tags$month = ""
final_tags$weekdays = ""
final_tags$date = ""
final_tags$timestamp = ""
final_tags$timezone = ""
final_tags$year = ""
final_tags$count = 1

#Extract from the time string
for (i in 1:nrow(final_tags)){
  final_tags[i,]$weekdays = final_tags$Weekday[[i]][1]
  final_tags[i,]$month = final_tags$Weekday[[i]][2]
  final_tags[i,]$date = final_tags$Weekday[[i]][3]
  final_tags[i,]$timestamp = final_tags$Weekday[[i]][4]
  final_tags[i,]$timezone = final_tags$Weekday[[i]][5]
  final_tags[i,]$year = final_tags$Weekday[[i]][6]
}
#Remove time string
final_tags$Weekday = NULL

#Group tags by month/tag to get a count of tags each month
bymonth = final_tags %>%
  group_by(month, tag) %>%
  summarise(counter = sum(count))
bymonth = bymonth %>%
  filter(counter > 5)
#Group tags and get count of tags overall (Apr - Nov)
overall = final_tags %>%
  group_by(tag) %>%
  summarise(counter = sum(count)) %>%
  filter(counter > 5)
#Filters
bymonth = filter(bymonth, !grepl("slide", tag))
bymonth = filter(bymonth, !grepl("the", tag))
bymonth = filter(bymonth, !grepl("of", tag))
bymonth = filter(bymonth, !grepl("picture", tag))
bymonth = filter(bymonth, !grepl("and", tag))
bymonth = filter(bymonth, !grepl("show", tag))
bymonth = filter(bymonth, !grepl("to", tag))
bymonth = filter(bymonth, !grepl("problem", tag))
bymonth = filter(bymonth, !grepl("for", tag))

overall = filter(overall, !grepl("slide", tag))
overall = filter(overall, !grepl("the", tag))
overall = filter(overall, !grepl("of", tag))
overall = filter(overall, !grepl("picture", tag))
overall = filter(overall, !grepl("and", tag))
overall = filter(overall, !grepl("show", tag))
overall = filter(overall, !grepl("to", tag))
overall = filter(overall, !grepl("problem", tag))
overall = filter(overall, !grepl("for", tag))

