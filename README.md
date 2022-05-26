# TDI_Capstone

## Summary
This project aims to design a web application that recommends running routes to users catered to their preferences. 

## Problem Statement
Runners like to explore different routes. Having this option helps to keep them motivated. There are a few apps with similar functionality in the market. However, they heavily rely on online reviews to generate routes; therefore, they miss crucial features that people do not post online, e.g., safety. This project aims to combine crowdsourced data with additional data, e.g., safety, to recommend running routes to users. 

## Project
At the heart of this problem is a weighted graph of the city of San Francisco that stores data relevant to running on each edge (i.e., each street segment). To create this graph, two main sources of data were used:
 
1. Structured data from publicly available sources:
  + Geographic data form OpenStreetMap API
  + Population data from US 2020 Census API
  + Crime data from San Francisco Police Department Incident Reports

2. Data scraped from online review sources:
  + Running Popularity data based on posts on MapMyRun

The first challenge was combining data from different sources. I used the latitude and longitude coordinates to join the datasets using nearest nodes. The rest of the project can be split to two parts:

1. Predicting the popularity of a route for running
2. Recommending routes to users based on the predicted popularity index and other users' preferences. 

To solve the first problem, I used the Random-Forst Regressor to predict the “running popularity index” for all the edges of the graph. Before implementing the model, some preprocessing and feature engineering were required. For instance, I used a demention reduction mthoed i.e., PCA to calculate a single crime index value for each edge of the graph. 

I used this predicted popularity index along with other features, to recommend routes. To this end, I found all the nodes in the ranges of users’s desired running distance and found the routes that optimized the cost function bellow:

 Cost Function =    (length cost)-(predicted popularity reward) + (crime cost)× (user_preference)- (parks reward)×(user_preference) + (traffic lights cost)×(user_preference) 

## Deliverables
bit.ly/RunLikeU
