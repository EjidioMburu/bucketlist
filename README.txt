# 1.PROJECT TITLE AND DISCRIPTION
    BucketList Application API->this is a project to create an API for an online Bucket List service using
    Flask. * A Bucket List is a list of things that one has not done
    before but wants to do before dying.*

# 2.MOTIVATION
    My aim for this project was to enhance and elevate the functionality of a Flask-based CRUD application

# 3.INSTALLATIONS
    ## install the following:
       Python 3.10.7(download python)
       in a directory called  bucketlist_project:
           Flask 2.3.2
       install pip install bcrypt
           bcrypt(pip install bcrypt)
           sqlarchemy(
            py -m pip install --upgrade pip 
            pip install sqlarchemy)
           CORS(pip install Flask-Cors)
           pip install PyJW

# 4.TECH/FRAMEWORK
     frontend->html5,css(bootstrap)
     backend->python(flask)
     database->(SQLArchemy),SQLite

# 5.USAGE
   DATABASE interactions
   => The project have used sqlite relation database and sqlarchemy as an Object Relational Mapper (ORM) library for Python which helps python to interact with the DB
     It have the following tables:
        a)USER which stores user information namely;id,username and password to enable registration and login process
        b)BUCKETLIST which stores bucketlist attributes 
        c)BUCKETLISTITEM which stores the attributes of a specific item for a specific bucketlist
    => FUCTIONALITIES
        Login->with http://127.0.0.1:5000/auth/login you are able to login using correct credentials.
        Registrations-> with http://127.0.0.1:5000/auth/register you are able to register as a new user.
        Creating a new bucketlist->http://127.0.0.1:5000/bucketlist/ enables to create a new bucketlist
        Listing all bucketlist->http://127.0.0.1:5000/bucketlists.
        Get a single bucketlist->http://127.0.0.1:5000/bucketlists/<int:id> it gives a specific bucketlist by providing the target id number on the url.
        Update this bucketlist->http://127.0.0.1:5000/bucketlists/<int:id> by inputing the target bucketlist id it updates.
        Delete this single bucket list->http://127.0.0.1:5000/bucketlists/<int:id> for deleting the target bucketlist.
        Create a new item in bucket list->http://127.0.0.1:5000/bucketlists/<int:id>/items/ creates a new item for a specific bucketlist.
        Update a bucket list item->http://127.0.0.1:5000/bucketlists/<int:id>/items/ able to edit a particular item for a specific bucketlist
        Delete an item in a bucket list->http://127.0.0.1:5000/bucketlists/<int:id>/items/ able to delete a particular item for a specific bucketlist
        ||||||||||||||||||||||
        http://127.0.0.1:5000/bucketlists after retriving all the bucketlist ,you can such a specific bucketlist via URL by providing a query eg. http://127.0.0.1:5000/bucketlists?q=r that link will return all bucketlist with letter "r" in it.
        By default the page returns results of 20  and the maximum number of results is 100

# 5.BUILD STATUS
    On the "all bucketlist page (http://127.0.0.1:5000/bucketlists) there was a bug on how to search using the provided user interface (html search bar)
# 6.SECURITY FEATURE
    Have ensured the routes are protected using security algorithm
# 7.FUTURE DEVELOPMENT
  
  intergrate reactjs and improve frontend
  host the project 
  



       


      