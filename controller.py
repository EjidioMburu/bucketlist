from flask import Flask,redirect,render_template,url_for,request,session,jsonify,flash,json
from flask_cors import CORS
#library to hash the password
from flask_bcrypt import Bcrypt 

#database
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref,declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.wrappers import Request


Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    
    password_hash = Column(String)
    #a method to do serialization(object to dictionary)
    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash =password_hash

    def to_dict(self):
        return {'username': self.username, 'password_hash': self.password_hash}


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
bcrypt = Bcrypt(app)
#application can now make requests to other domains, and those domains can make requests to your application
CORS(app)
app.secret_key = 'gvhvh54..gv'


@app.route('/bucketlists/<int:id>/items/', methods=['GET'])
# route to create new item for particular bucketlist
def create_bucketlist_item(id):
    session = Session()
    bucketlist = session.query(BucketList).get(id)
    session.close()
    if bucketlist:
        return render_template('create_bucketlist_item.html', bucketlist=bucketlist)
    return jsonify({"error": "Bucketlist not found"}), 404





#login a user in
@app.route('/auth/login')
def login_page():
    return render_template('login.html')
@app.route('/login', methods=['GET','POST'])
def login_route():
    # Get username and password from the form
    username = request.form.get('username')
    password = request.form.get('password')
    # Create a session
    session = Session()
    # Query for the user
    user = session.query(User).filter(User.username == username).first()
    # Convert user data to a dictionary
    user_dict = user.to_dict()
    if user_dict is not None:
        
        password_hash = user_dict["password_hash"]
    #algorithm which compares the hash of the input password with the stored hash
        if bcrypt.check_password_hash(password_hash, password):
            session.close()
            return redirect(url_for('list_bucketlists'))
        else:
            session.close()
            flash("wrong credentials")
            return redirect(url_for('login_page'))  # Redirect to a login page with an error message.
        

#register a new user
@app.route('/auth/register', methods=['GET', 'POST'])
def register():
    # logic
    if request.method == "POST":
        # assigns the newly created session instance to the variable
        session = Session()

        username = request.form["username"]
        password = request.form["password"]
        #to hash the password using bcrypt library
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
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
    

# a route to add/create a new bucketlist
@app.route('/bucketlist/add', methods=['GET'])
def create_new_bucketlist():
    return render_template("create_bucketlist.html")    
#creating a new bucketlist
@app.route('/bucketlists/', methods=["GET","POST"])
def create_bucketlist():
    
    if request.method == 'POST':
        
        bucketlist_name = request.form['bucketlist_name']
        
        item_name = request.form['item_name']
        done = True if request.form.get('done') == 'on' else False

        new_bucket_list = BucketList(
            name=bucketlist_name,
            
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
    
    
#list all the created bucket list
# Route to list all created bucket lists
@app.route('/bucketlists', methods=['GET'])
def list_bucketlists():
    session = Session()
    # Get the 'limit' parameter from the request, or use a default value of 20
    limit = int(request.args.get('limit', 20))
    # Ensure that 'limit' is within the specified range (1 to 100)
    limit = max(1, min(limit, 100))
     # Get the search query from the 'q' parameter
    search_query = request.args.get('q', '')
    # retrieve a list of items
    items = session.query(BucketList.name, BucketListItem.name, BucketList.id).join(BucketList.items).filter(BucketList.name.ilike(f'%{search_query}%')).limit(limit).all()
    # Create a list to store unique bucket lists
    unique_bucket_lists = []
    for item in items:
        # Check if the bucket list ID has already been processed
        if item[2] not in [bl['bucketlist_id'] for bl in unique_bucket_lists]:
            unique_bucket_lists.append({
                "bucketlist_id": item[2],
                "bucketlist_name": item[0],
                "items": []
            })
            # Find the corresponding bucket list in unique_bucket_lists
            bucket_list = next(bl for bl in unique_bucket_lists if bl['bucketlist_id'] == item[2])
            # Add item details to the bucket list
            bucket_list["items"].append({
            "item_name": item[1],
            })              
    # Pass unique_bucket_lists to the template
    return render_template('bucket_lists.html', bucketlist_items=unique_bucket_lists)
    session.close()
    

# get individual bucketlist with a given id
@app.route('/bucketlists/<int:id>', methods=['GET'])
def get_bucketlist(id):
    session = Session()
    bucketlist = session.query(BucketList).get(id)
    session.close()
    if bucketlist:
        return render_template('single_update_bucket.html', bucketlist=bucketlist)
    return jsonify({"error": "Bucketlist not found"}), 404
    

#editing/update single/specific bucketlist 
@app.route('/bucketlists/<int:id>', methods=['PUT'])
def update_bucketlist(id):
    session = Session()
    bucketlist = session.query(BucketList).get(id)
    if not bucketlist:
        session.close()
        return jsonify({"error": "Bucketlist not found"}), 404

    if request.method == 'PUT':
        bucketlist.name = request.form.get('name', bucketlist.name)

        try:
            session.commit()
            session.close()  
            flash('Bucketlist updated successfully!!!')
            return render_template('single_update_bucket.html', id=id)
        except Exception as e:
            session.rollback()
            session.close()
            return jsonify({"error": str(e)}), 500
    
    return render_template('update_bucketlist_form.html', bucketlist=bucketlist)


#delete a particular bucketlist
@app.route('/bucketlists/<int:id>', methods=['DELETE','POST'])
def delete_bucketlist(id):
    session = Session()
    bucketlist = session.query(BucketList).get(id)
    if bucketlist:
        session.delete(bucketlist)
        session.commit()
        flash("one bucketlist parmanently deleted")
        return redirect(url_for('list_bucketlists'))
    else:
        return 'Bucketlist not found', 404

#create a new item in bucket list
@app.route('/bucketlists/<int:id>/items/', methods=['POST'])
def create_item(id):
    # creat a new item
    item_name = request.form['item_name']  # Assuming JSON request
    done = done = True if request.form.get('done') == 'on' else False
    # Finding the corresponding bucket list
    bucket_list = session.query(BucketList).get(id)
    if bucket_list:
        # Create a new item
        new_item = BucketListItem(
            name=item_name,
            done=done,
            bucket_list=bucket_list
        )
        # Add the new item to the session and commit
        session.add(new_item)
        session.commit()
        flash("Item added successfully")
        return redirect(url_for('list_bucketlists'))
    else:
        return jsonify({"error": "Bucket List not found."}), 404
    

#route to update and delete a particular item for a particular bucketlist
@app.route('/bucketlists/<int:id>/items/<int:item_id>',methods=['GET'])
def update_delete_item(id,item_id):
    session=Session()
    bucketlist = session.query(BucketList).get(id)
    
    item = session.query(BucketListItem).filter_by(id=item_id).first()
    
    return render_template('update_delete_item.html', bucketlist=bucketlist, item=item)

#update a particular bucket list item 
@app.route('/bucketlists/<int:id>/items/<int:item_id>', methods=['PUT'])
def update_item(id, item_id):
    bucketlist = session.query(BucketList).get(id)
    item = session.query(BucketListItem).filter_by(id=item_id).first()
    if not bucketlist:
        session.close()
        return jsonify({"error": "Bucketlist not found"}), 404
    if request.method == 'PUT':
        item.name = request.form.get('item_name', item.name)
        try:
            session.commit()
            flash('Item updated successfully!') 
            session.close() 
            return redirect(url_for('update_delete_item.html', bucketlist=bucketlist, item=item))
        except Exception as e:
            session.rollback()
            session.close()
            return jsonify({"error": str(e)}), 500
    return render_template('update_bucketlist_form.html', bucketlist=bucketlist)


    #delete a particular item from a specific bucketlist
@app.route('/bucketlists/<int:id>/items/<int:item_id>', methods=['DELETE', 'POST'])
def delete_item(id, item_id):
    if request.form.get('_method') == 'DELETE':
        item_id=str(item_id)
        item = session.query(BucketListItem).filter_by(id=item_id).first()
        if not item:
            return jsonify({"error": "Item not found"}), 404
        try:
            session.delete(item)
            session.commit()
            flash('Item deleted successfully', 'success')
            session.close()
            return redirect(url_for('get_bucketlist', id=id))
        except Exception as e:
            session.rollback()
            session.close()
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({'error': 'Wrong method'}), 405


if __name__ == '__main__':
    app.run(debug=True)
