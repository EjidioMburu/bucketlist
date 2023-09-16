from flask import Flask,redirect,render_template,url_for,request,session,jsonify,flash
from werkzeug.security import generate_password_hash, check_password_hash

#database
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref,declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData
from passlib.hash import bcrypt  # For password hashing
from sqlalchemy.orm import sessionmaker
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.wrappers import Request





Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    
    password_hash = Column(String)

class BucketList(Base):
    __tablename__ = 'bucketlists'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    date_modified = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(String)
    
    #defines one to many relationship
    items = relationship("BucketListItem", back_populates="bucket_list")

class BucketListItem(Base):
    __tablename__ = 'bucketlist_items'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    date_modified = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    done = Column(Boolean)
    bucket_list_id = Column(Integer, ForeignKey('bucketlists.id'))
    
    #defines one to many relationship
    #allows you to access the items associated with a specific bucket list instance using the items attribute, 
    # and it also allows you to access the corresponding 
    # bucket list for a specific item using the "bucket_list" attribute in the BucketListItem class.
    bucket_list = relationship("BucketList", back_populates="items")

 #indicates database dialect and connection arguments

engine = create_engine('sqlite:///bucketlist.db', echo=True)
#create the tables in the database based on the defined models

Base.metadata.create_all(engine)
#allows to make queries through session
Session = sessionmaker(bind=engine)
session = Session()

#creating an instance of class flask
app = Flask(__name__)
app.secret_key = 'gvhvh54..gv'

# Sample data to store bucket lists and items (replace this with your database or data storage logic).
bucketlists = [{"id":1,"name":"ejidio","item":[]}]
items_counter = 1


#middleware to handle the _method field and override the HTTP method for DELETE and PUT requests:
class MethodRewriteMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request = Request(environ)
        if request.method == 'POST':
            method = request.form.get('_method', '').upper()
            if method in ['PUT', 'DELETE']:
                environ['REQUEST_METHOD'] = method
        return self.app(environ, start_response)

app.wsgi_app = MethodRewriteMiddleware(app.wsgi_app)

#route to views
@app.route('/bucketlist/add')
def create_new_bucketlist():
    return render_template("create_bucketlist.html")


# Helper function to find a bucket list by its ID
def find_bucketlist_by_id(bucketlist_id):
    return next((bucketlist for bucketlist in bucketlists if bucketlist['id'] == bucketlist_id), None)



#login a user in
@app.route('/auth/login')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['GET','POST'])
def login_route():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Create a session
    session = Session()
    
    # Query for the user
    user = session.query(User).filter_by(username=username).first()
    
    
    if user:
        return redirect(url_for(list_bucketlists))
        # user_data = {
            
        #     'password': user.username,
        #     # Add other user attributes here as needed
        # }
        # jsonify(user_data)
        
     
    # and bcrypt.check_password_hash(user.password_hash, password):
    #     session.close()
    #     flash("Login successful!")
    #     return   '# Redirect to a success page or perform some action.'
    
    session.close()
    flash("Invalid username or password.")
    return redirect(url_for('login_page'))  # Redirect to a login page with an error message.



@app.route('/auth/register', methods=['GET', 'POST'])

def register():
    # logic
    if request.method == "POST":
        # assigns the newly created session instance to the variable
        session = Session()

        username = request.form["username"]
        password = request.form["password"]

        password_hash = bcrypt.hash(password)
        new_user = User(username=username, password_hash=password_hash)
        session.add(new_user)

        try:
            session.commit()
            flash('Registration successful! login Here')  # Corrected here
            return redirect(url_for('login_page'))
            
        except Exception as e:
            session.rollback()
            return jsonify({'message': 'Registration failed', 'error': str(e)}), 400
        finally:
            session.close()


        return jsonify({"message": "User registered successfully"}), 201
    
    else:

        return render_template("register_form.html")

    
#creating a new bucket list
@app.route('/bucketlists', methods=["POST"])
def create_bucketlist():
    
    if request.method == 'POST':
        bucketlist_name = request.form['bucketlist_name']
        item_name = request.form['item_name']
        done = True if request.form.get('done') else False

        new_bucket_list = BucketList(
            name=bucketlist_name,
            created_by="1113456",
            items=[
                BucketListItem(
                    name=item_name,
                    done=done
                )
            ]
        )

        session.add(new_bucket_list)
        session.commit()
        # Redirect to the route that lists all created bucket lists
        return redirect(url_for('list_bucketlists'))
    return render_template('create_bucketlist.html')
    

    

#list all the created bucket list
# Route to list all created bucket lists
@app.route('/bucketlists/', methods=['GET'])
def list_bucketlists():
    # Logic to fetch and list all bucket lists
    session = Session()

    # Query to retrieve bucketlist names along with their corresponding item names
    query = session.query(BucketList.name, BucketListItem.name).join(BucketList.items)

    # Fetch the data
    result = query.all()
    #convert the result into a list of dictionaries before sending it as a JSON response
    #bucket_name and item_name acts as keys to the dictionally
    bucketlist_items = [{"bucketlist_name": row[0], "item_name": row[1]} for row in result]
    

     # Render the template and pass the 'bucketlist_items' data as a context variable
    return render_template('bucket_lists.html', bucketlist_items=bucketlist_items)
    
    session.close()


@app.route('/bucketlists/<int:id>', methods=['GET'])
def get_bucketlist(id):
    session = Session()
    bucketlist = session.query(BucketList).get(id)
    session.close()
    if bucketlist:
        return render_template('single_update_bucket.html', bucketlist=bucketlist)
    return jsonify({"error": "Bucketlist not found"}), 404

#editing/update single/specific bucketlist 
@app.route('/bucketlists/<int:id>/update', methods=['POST'])
def update_bucketlist(id):
    session = Session()
    bucketlist = session.query(BucketList).get(id)
    if bucketlist:
        bucketlist.name = request.form['name']
        session.commit()
        session.close()
        return redirect('/bucketlists/')
    session.close()
    return 'Bucketlist not found', 404
@app.route('/bucketlists/<int:id>', methods=['DELETE'])
def delete_bucketlist(id):
    session = Session()
    bucketlist = session.query(BucketList).get(id)
    if request.method == 'DELETE':
       session.delete(bucketlist)
       session.commit()
       return redirect('/bucketlists/')
    return 'Bucketlist not found', 404


#create a new item in bucket list
@app.route('/bucketlists/<int:id>/items/', methods=['PUT'])
def create_item(id):
    bucketlist = find_bucketlist_by_id(id)
    if not bucketlist:
        return jsonify({"message": "Bucket list not found"}), 404

    data = request.get_json()
    item_name = data.get('name')
    if not item_name:
        return jsonify({"message": "Item name is required"}), 400

    global items_counter
    new_item = {
        "id": items_counter,
        "name": item_name
    }
    items_counter += 1
    bucketlist['items'].append(new_item)

    return jsonify({"message": "Item created successfully", "item": new_item}), 201

#update a bucket list item 
@app.route('/bucketlists/<int:id>/items/<int:item_id>', methods=['PUT'])
def update_item(id, item_id):
    bucketlist = find_bucketlist_by_id(id)
    if not bucketlist:
        return jsonify({"message": "Bucket list not found"}), 404

    item = next((i for i in bucketlist['items'] if i['id'] == item_id), None)
    if not item:
        return jsonify({"message": "Item not found"}), 404

    data = request.get_json()
    item_name = data.get('name')
    if not item_name:
        return jsonify({"message": "Item name is required"}), 400

    item['name'] = item_name
    return jsonify({"message": "Item updated successfully", "item": item}), 200

#delete an item in bucket item

@app.route('/bucketlists/<int:id>/items/<int:item_id>', methods=['DELETE'])
def delete_item(id, item_id):
    bucketlist = find_bucketlist_by_id(id)
    if not bucketlist:
        return jsonify({"message": "Bucket list not found"}), 404

    item = next((i for i in bucketlist['items'] if i['id'] == item_id), None)
    if not item:
        return jsonify({"message": "Item not found"}), 404

    bucketlist['items'] = [i for i in bucketlist['items'] if i['id'] != item_id]
    return jsonify({"message": "Item deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
