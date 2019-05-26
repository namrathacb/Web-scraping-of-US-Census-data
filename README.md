# topos

1. Python and BeautifulSoup package is used for the assignment.

2. Defined a function(parse_data_from_table) which sends a connetion request to  the Wikipedia page. HTML response obtained  is Parsed to     get the table contents and stored it in the form of a list.

3. Collected population Census data of different cities in the United States as estimated by United States Census Bureau using the          function defined and converted the list into a data frame.

4. From the data frame, each city's wikipedia link is stored. Using these URL's, HTML response is recorded for each city.

5. From each HTML response ,two  tables  containing the City's government information,website  and racial compostion are parsed.

6. Information from the twop tables are concatenated with the original data frame against each City.

7. Exported into a CSV file which can uploaded to a BigQuery Table.
