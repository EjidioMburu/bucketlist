from flask import Flask,redirect,render_template,url_for,request,session
app=Flask(__name__)
app.secret_key="wdjnwu"
@app.route("/")
def home():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register_form.html")

@app.route("/bucketlist")
def bucketlist():
    return render_template("bucket_lists.html")

@app.route("/single")
def single():
    
    return render_template("single_bucket.html")


if __name__ == "__main__":
   app.run(debug=True)

