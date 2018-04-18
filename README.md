###FULL REQUIREMENTS
- **Has all setup necessary to run Flask application and runs on port 5000**
- **User should be able to load route '/'**
- Include navigation in base.html with href links to all navigatable pages
- **All templates inherit from base.html (include at least one additional block)**
- **Uses user authentication (HW4)**
- Data associated with a user and at least 2 routes besides "logout" that can only be seen by logged-in users
- **3 model classes besides "User" class**
- **At least 1 1:many relationship between 2 models**
- **At least 1 many:many relationship between 2 models**
- **Successfully save data to each table**
- Successfully query data from each of your models (must be visible by user)
- **At least 1 query of all data using .all() which is displayed in a template**
- **At least 1 query using .filter_by(...)**
- **At least 1 helper function (besides get_or_create)**
- **At least 2 get_or_create functions**
- At least 1 error handler for a 404 error and corresponding template
- At least one error handler for any other error (like 500) and corresponding template
- **At least 4 template .html files (besides error templates)**
- **At least 1 Jinja template for loop**
- **At least 2 Jinja template conditionals**
- **At least 1 request to a REST API depending on WTForm submit data**
- **Process API data and saves to database**
- **At least 1 GET request to a new page**
- **At least 1 POST request to the same page (excluding login/registration)**
- **At least 1 POST request to a new page (excluding login/registration)**
- **At least 2 custom validators excluding log in/auth code**
- **At least 1 method to update items saved in database**
- At least 1 method to delete items saved in database
- **At least 1 use of "redirect"**
- **At least 2 uses of "url_for"**
- **At least 5 view functions**
###EXTRA CREDIT REQUIREMENTS
- **Include AJAX request that accesses and displays useful data**
- Create, run, and commit at least one migration
- Include file upload in your application and save/use results of the file
- Deploy application to Internet or Heroku: (INSERT URL HERE)
- Implement user sign-in with OAuth service and include that you need a specific-service account in the README in the same section as the list of modules that must be installed
###DESCRIPTION OF APPLICATION
This application allows users to search for images on the Getty API (http://developers.gettyimages.com/en/trytheapi.html?) and search and save for their favorite photos. Users can see all of the possible images that have been searched (and the users that have saved the specific images) as well as their search history (by search term) and folders that they have created for each specific photos (they can save photos to various folders). Users can search for other users and see their search history. (Essentially something like Imgur except the users don't upload any photos.)
###MODULES INSTALLED WITH PIP
###ROUTES (AND THEIR RESPECTIVE HTML PAGES OR WHAT IT DOES)
