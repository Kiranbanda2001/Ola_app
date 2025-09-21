## 🚖 Ola Rides - Interactive Analytics Dashboard
The OLA Data Analyst Project analyzes ride-booking data using SQL and Power BI to track ride volumes, customer behavior, and driver performance. It focuses on booking statuses, revenue breakdowns by payment method, and top customers. SQL queries are used to calculate ride statistics, and the final Power BI dashboard visualizes key data, including ride volumes, vehicle performance, and sales. The analysis helps optimize OLA's services by identifying trends and areas for improvement.

## 🔍 Project Overview
This project simulates real-world ride-calling data and includes 20+ fields such as:

Date & Time: Tracks booking trends and peak hours.

Booking ID: Unique identifier for each ride (e.g., CNR12345678).

Booking Status: Status of the ride (e.g., Success, Cancelled by Customer, etc.).

Customer_ID: ID of the customer who booked the ride.

Vehicle_Type: Type of vehicle used (e.g., Prime Sedan, Auto, etc.).

Pickup & Drop Locations: Randomized across 50 prominent areas in Bengaluru.

V_TAT (Vehicle Turnaround Time): Represents the duration taken by a vehicle between consecutive rides, indicating operational efficiency.

C_TAT (Customer Turnaround Time): Represents the total time taken from when a customer books a ride until the ride is completed, reflecting service experience.

Canceled_Rides_by_Customer: Number of rides canceled by customers after booking.

Canceled_Rides_by_Driver: Number of rides canceled by drivers after accepting the booking.

Incomplete_Rides: A flag to indicate whether the ride was completed or not.

Incomplete_Rides_Reason: If the ride was incomplete, this column stores the reason.

Booking_Value: Monetary value of the completed ride.

Payment_Method: Mode of payment used for the ride (e.g., UPI, Card, Cash).

Ride_Distance: Distance covered in the ride (in kilometers).

Driver_Ratings: Ratings provided by customers to the drivers (out of 5).

Customer_Rating: Ratings provided by drivers to the customers (out of 5).

## 🛠️ Tools & Technologies
SQL: Data wrangling, cleaning and querying for insights.
Power BI: Dashboard creation and detailed reporting.
Python/Excel: Data preprocessing and randomization.

## 📂 SQL Queries
All SQL queries used in this project are stored separately in SQL_Queries.txt.
You can review them independently to understand the exact data extraction and transformations applied.

## 📂 Power Bi Dashboard
Interactive dashboards are built in Power BI to visualize key metrics like revenue, cancellations, ratings, and booking patterns.

🔎 For detailed insights, interpretations, and recommendations, please open the ola ride project.pbix report included in this repository.


