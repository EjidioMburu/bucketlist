from flask import Flask,redirect,render_template,url_for,request,session,request,jsonify

#creating an instance of class flask
app = Flask(__name__)

# Sample data to store bucket lists and items (replace this with your database or data storage logic).
bucketlists = [{"id":1,"name":"ejidio","item":[]}]
items_counter = 1

# Helper function to find a bucket list by its ID
def find_bucketlist_by_id(bucketlist_id):
    return next((bucketlist for bucketlist in bucketlists if bucketlist['id'] == bucketlist_id), None)

#login a user in
@app.route('/auth/login', methods=['POST'])
def login():
    # logic 
    return jsonify({"message": "Login successful"}), 200

#register a user
@app.route('/auth/register', methods=['POST'])
def register():
    #  logic
    return jsonify({"message": "User registered successfully"}), 201

#creating a new bucket list
@app.route('/bucketlists/', methods=['POST'])
def create_bucketlist():
    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({"message": "Bucket list name is required"}), 400

    global items_counter
    new_bucketlist = {
        "id": len(bucketlists) + 1,
        "name": name,
        "items": []
    }
    bucketlists.append(new_bucketlist)

    return jsonify({"message": "Bucket list created successfully", "bucketlist": new_bucketlist}), 201

#list all the created bucket list
@app.route('/bucketlists/', methods=['GET'])
def list_bucketlists():
    return jsonify(bucketlists), 200

#get single/specific bucket list
@app.route('/bucketlists/<int:id>', methods=['GET'])
def get_bucketlist(id):
    bucketlist = find_bucketlist_by_id(id)
    if not bucketlist:
        return jsonify({"message": "Bucket list not found"}), 404

    return jsonify(bucketlist), 200

#editing/update single/specific bucketlist 
@app.route('/bucketlists/<int:id>', methods=['PUT'])
def update_bucketlist(id):
    bucketlist = find_bucketlist_by_id(id)
    if not bucketlist:
        return jsonify({"message": "Bucket list not found"}), 404

    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({"message": "Bucket list name is required"}), 400

    bucketlist['name'] = name
    return jsonify({"message": "Bucket list updated successfully", "bucketlist": bucketlist}), 200


#delete a single bucketlist
@app.route('/bucketlists/<int:id>', methods=['DELETE'])
def delete_bucketlist(id):
    global bucketlists
    bucketlist = find_bucketlist_by_id(id)
    if not bucketlist:
        return jsonify({"message": "Bucket list not found"}), 404

    bucketlists = [i for i in bucketlists if i['id'] != id]
    return jsonify({"message": "Bucket list deleted successfully"}), 200

#create a new item in bucket list
@app.route('/bucketlists/<int:id>/items/', methods=['POST'])
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
