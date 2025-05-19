from flask import Flask, render_template,url_for,request,redirect
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__) # can set templates and static to different stuff by putting args template_folder = "", static_folder = "my_static"
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class entry(db.Model):
    id = db.Column(db.Integer,primary_key = True) # var name = db.Column(Content, modifications) primary_key is a unique identifier for a column
    content = db.Column(db.String(1000),nullable = False) # nullable means that it cannot be empty
    trans = db.Column(db.String(1000),nullable = False)
    typ = db.Column(db.String(200),nullable = False )

    def __repr__(self):
        return '<Task %r>' %self.id

@app.route('/', methods=['POST','GET'])
def index():
    return render_template('home.html')

@app.route('/import_file',methods = ["POST","GET"])
def import_file():
    if request.method == "POST":
        uploaded_file = request.files.get('file')
        if not uploaded_file:
            return "No file uploaded"

        try:
            lines = uploaded_file.read().decode('utf-8').splitlines()
            for line in lines:
                ls = [s.strip() for s in line.split(",")]
                if len(ls) != 3:
                    continue 
                new_content = entry(content=ls[0], trans=ls[1], typ=ls[2])
                db.session.add(new_content)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            return f"There was an error importing: {e}"

    return redirect('/')

@app.route('/show', methods=['POST','GET'])
def show():
    entries = entry.query.order_by(entry.content).all()
    return render_template('show.html',entries = entries)
    

@app.route('/insert',methods = ['POST','GET'])
def insert():
    if request.method == "POST":
        c = request.form['content']
        t = request.form['translation']
        tp = request.form['type']
        new_content = entry(content = c, trans = t,typ = tp)

        try: 
            db.session.add(new_content)
            db.session.commit()
            return redirect("/")
        except:
            return "There was an error adding"
    else:
        return render_template('insert.html')

@app.route('/delete_all', methods=['POST'])
def delete_all():
    try:
        num_deleted = entry.query.delete()
        db.session.commit()
        return redirect('/')
    except Exception as e:
        return f"There was an error deleting all entries: {e}"


@app.route('/delete/<int:id>')
def delete(id):
    entry_to_delete = entry.query.get_or_404(id)
    try:
        db.session.delete(entry_to_delete)
        db.session.commit()
        return redirect('/show')
    except:
        return "There was an error deleting"
    
@app.route('/translate', methods = ["GET","POST"])
def translate():
    correct = False
    submitted = False
    
    if request.method == "POST":
        if 'next' in request.form:
            random_trans = entry.query.filter_by(typ="translation").order_by(db.func.random()).first()
            return render_template('translate.html', trans=random_trans, correct=False,submitted = False)

        trans_id = request.form['trans_id']
        user_entry = request.form['user_trans']
        current_trans = entry.query.get(int(trans_id))
        submitted = True

        correct_percentage = 0
        user_words = user_entry.strip().lower().split()
        target_words = current_trans.trans.strip().lower().split()

        match_count = sum(1 for word in user_words if word in target_words)
        correct_percentage = (match_count/ len(target_words)) * 100
        
        if correct_percentage >35:
            correct = True
        
        return render_template('translate.html', trans=current_trans, correct=correct , submitted = submitted)

    random_trans = entry.query.filter_by(typ="translation").order_by(db.func.random()).first()
    return render_template('translate.html', trans=random_trans, correct=False ,submitted = False)
        

@app.route('/grammar')
def grammar():
    # give phrases, fix phrases or create phrases using grammar
    random_grammar = entry.query.filter_by(typ = "grammar").order_by(db.func.random()).first()
    try:
        return render_template('grammar.html', grammar = random_grammar)
    except:
        return "No grammar available"
    

@app.route('/vocab')
def vocab():
    random_vocab = entry.query.filter_by(typ = "vocab").order_by(db.func.random()).first()
    try:
        return render_template('vocab.html', vocab = random_vocab)
    except:
        return "No vocab available"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)



#Translating passages website, pull from a database of passages from random texts organised in JLPT levels, books, maybe include ai to test similarity %
# work on separation of dbs, search algo, filters