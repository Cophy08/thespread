library(XML)
library(sampling)
library(plyr)
library(arm)

firstyears <- list()

# Scrape first-year QBs for the years
# Using 1980 - 2012 for "modern passing era"

years <- seq(1980, 2012)

for (i in seq_along(years)) {
  url <- paste("http://www.pro-football-reference.com/play-index/psl_finder.cgi?request=1&match=single&year_min=",
               years[i], "&year_max=", years[i], "&season_start=1&season_end=1&age_min=0&age_max=99&league_id=&team_id=&is_active=&is_hof=&pos_is_qb=Y&c1stat=&c1comp=gt&c1val=&c2stat=&c2comp=gt&c2val=&c3stat=&c3comp=gt&c3val=&c4stat=&c4comp=gt&c4val=&order_by=pass_td&draft=0&draft_year_min=1936&draft_year_max=2012&type=&draft_round_min=0&draft_round_max=99&draft_slot_min=1&draft_slot_max=500&draft_pick_in_round=0&draft_league_id=&draft_team_id=&college_id=all&conference=any&draft_pos_is_qb=Y&draft_pos_is_rb=Y&draft_pos_is_wr=Y&draft_pos_is_te=Y&draft_pos_is_rec=Y&draft_pos_is_t=Y&draft_pos_is_g=Y&draft_pos_is_c=Y&draft_pos_is_ol=Y&draft_pos_is_dt=Y&draft_pos_is_de=Y&draft_pos_is_dl=Y&draft_pos_is_ilb=Y&draft_pos_is_olb=Y&draft_pos_is_lb=Y&draft_pos_is_cb=Y&draft_pos_is_s=Y&draft_pos_is_db=Y&draft_pos_is_k=Y&draft_pos_is_p=Y",
               sep = "")
  yearData <- readHTMLTable(url, header = FALSE)$stats
  names(yearData)[2] <- "name"
  names(yearData)[3] <- "firstyear"
  firstyears[[i]] <- yearData
}

firstyear.dataDF <- ldply(firstyears, data.frame) # Combine into single data frame

alldata <- list()

# Scrape all passing statistics for the years, not just for rookies
for (i in seq_along(years)) {
  url <- paste("http://www.pro-football-reference.com/years/", years[i], "/passing.htm", sep = "")
  yearData <- readHTMLTable(url)
  yearData <- transform(yearData, year = years[i])
  alldata[[i]] <- yearData
}

names <- c("rank", "name", "team", "age", "games", "games.started", 
           "record", "completions", "attempts", "completion.pct", "yards", "td",
           "td.pct", "int", "int.pct", "long", "ypa", "adj.ypa", "yp.completion", 
           "yp.game", "rating", "sacks", "sack.yards", "net.ypa", "adj.nypa",
           "sack.pct", "q4.comeback", "gwd", "year", "qbr")

all.dataDF <- ldply(alldata, data.frame) # Combine into single data frame
names(all.dataDF) <- names

# Need to consolidate names (some have * at end, some don't)
all.dataDF$name <- gsub('\\*|\\*\\+', '', all.dataDF$name)
blanks <- which(all.dataDF$name == "")
all.dataDF <- all.dataDF[-blanks,]

firstyears <- firstyear.dataDF[,c("name", "firstyear")]
dataDF <- merge(all.dataDF, firstyears)

dataDF[, c(4,5, 6, 8:31)] <- sapply(dataDF[,c(4,5,6,8:31)], function(x) as.numeric(as.character(x)))
dataDF <- transform(dataDF, season = (year - firstyear) + 1) # Create season year variable 
dataDF <- ddply(dataDF, .(name), transform, lastyear = max(year)) # Create last year variable

# Create indicator for players who started half or more of a season's games
dataDF <- ddply(dataDF, .(name), transform, avgStarts = mean(games.started)) 
dataDF$starter <- NA
dataDF$starter[dataDF$avgStarts > 8] <- 1
dataDF$starter[dataDF$avgStarts <= 8] <- 0

# Indicator for rookies
dataDF$rookie <- 0
dataDF[dataDF$firstyear == 2012,]$rookie <- 1

model <- lmer(formula = adj.nypa ~ age + I(age^2) + (age | name), data = dataDF) 
BIC(model)

model1 <- lmer(formula = adj.nypa ~ age + I(age^2) + (age + I(age^2) | name), data = dataDF)
BIC(model1)

model2 <- lmer(formula = adj.nypa ~ age + I(age^2) + starter + (age + I(age^2) | name), data = dataDF) 
BIC(model2) 

model3 <- lmer(formula = adj.nypa ~ age + I(age^2) + starter + (age + I(age^2) + starter | name), data = dataDF) 
BIC(model3)

model3 <- lmer(formula = adj.nypa ~ age + I(age^2) + starter + (age + I(age^2) + starter | name), data = dataDF) 
BIC(model3)

# 2013 results
# Luck: 6.06
# Weeden: 4.51 (8 games)
# Osweiler: 4.83 (4 games)
# Cousins: 3.67 (5 games)
# Foles: 9.18 (not listed as starter)
# Wilson: 7.10
# Lindley: 0 games
# Tannehill: 5.00

# Fourth year players

third_years <- dataDF[dataDF$firstyear == 2010 & dataDF$lastyear == 2012, c('name', 'age', 'starter', 'adj.nypa')]
third_years$pred_2013 <- predict(model3, newdata = third_years)
ddply(third_years, .(name), numcolwise(max))

# Daniel: 5.3 (5 games)
# McCoy: 13 (1 game)
# Skelton: 0, no games
# Smith: 0, no games
# Bradford: 6.1, 7 games (injury)
# Tebow: 0, no games
