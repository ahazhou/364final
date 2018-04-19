###FULL REQUIREMENTS
- **Has all setup necessary to run Flask application and runs on port 5000**
- **User should be able to load route '/'**
- **Include navigation in base.html with href links to all navigatable pages**
- **All templates inherit from base.html (include at least one additional block)**
- **Uses user authentication (HW4)**
- **Data associated with a user and at least 2 routes besides "logout" that can only be seen by logged-in users**
- **3 model classes besides "User" class**
- **At least 1 1:many relationship between 2 models**
- **At least 1 many:many relationship between 2 models**
- **Successfully save data to each table**
- **Successfully query data from each of your models (must be visible by user)**
- **At least 1 query of all data using .all() which is displayed in a template**
- **At least 1 query using .filter_by(...)**
- **At least 1 helper function (besides get_or_create)**
- **At least 2 get_or_create functions**
- **At least 1 error handler for a 404 error and corresponding template**
- **At least one error handler for any other error (like 500) and corresponding template**
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
- **At least 1 method to delete items saved in database**
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
###APPLICATION USAGE
- While not logged in, you can only access the home page as well as the page that displays the results of your search
- Putting in a search term and clicking enter shows the top 50 images given by the Getty API
- On the home page, it shows the current user's search history as well as recently saved images by the community
- Since lots of the web pages cannot be directly accessed, there's only a few navigatable routes
- After searching for a term, you are presented a page that shows the picture's name, the picture itself (when clicked on, directs you to the picture's source), as well as a button to add to your favorites
- While not being logged in, you will be directed to a log in page
- On the add to favorites page (that is not directly accessible), you create a new folder by clicking on the create button, which then creates the folder for you
- To add an image to a folder, you click on the folder itself. Each specific image can only be added to a folder once.
- While being logged in, on the navigation links, a new link will pop up: "[INSERT USERNAME]'s Folders" that show you all of the folders that the user has created
- On the user's folders page, you can delete the folder by clicking delete or look at the images by clicking on the folders themselves.
- After clicking on the folder, you will be able to see all of the images that the user added as well as the option to delete the image.
###MODULES INSTALLED WITH PIP
- Everything used during class
###ROUTES (AND THEIR RESPECTIVE HTML PAGES OR WHAT IT DOES)
/ => /index
- Redirects to the index route because they shouldn't be separate
/index => index.html
- Can search for image
- Shows user search history
- Shows any image anyone added to a folder
- 