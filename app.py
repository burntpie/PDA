from flask import Flask, render_template, url_for, request, redirect, flash
from flask_pymongo import PyMongo
# from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from modeling import *

app = Flask(__name__)
app.config["SECRET_KEY"] = '1da204f539bfd15c3c5a85e1397f8052'
app.config["MONGO_URI"] = "mongodb://localhost:27017/local"
mongo = PyMongo(app)

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        return redirect('/')
    else:
        return render_template('index.html')


@app.route('/results/DA', methods=['POST', 'GET'])
def results_DA():
    if request.method == 'POST':
        return redirect('/')
    else:
        result_DA = mongo.db.result_DA
        DAs = []
        for DA in result_DA.find().sort("date_created", -1):
            DA["_id"] = str(DA["_id"])
            DA["date_created"] = DA["date_created"].strftime("%b %d %Y %H:%M:%S")
            DAs.append(DA)

        print(DAs)
        return render_template('result-DA.html', DAs=DAs)


@app.route('/results/DA/<id>', methods=['POST', 'GET'])
def results_DA_id():
    if request.method == 'POST':
        return redirect('/')
    else:
        result_DA = mongo.db.result_DA
        
        return render_template('index.html')


@app.route('/disinformation-analysis', methods=['POST', 'GET'])
def disinformation_analysis():
    if request.method == 'POST':
        try:
            res_dict = request.form.to_dict()
            input_text = res_dict['text']
            res_keys = list(res_dict)
            res_keys.pop(0)

            article_list, search_term, true_score = misinformation_check(input_text, res_keys, int(res_dict['article_count']))

            insert_dict = {
                "input_text" : input_text,
                "search_term" : search_term,
                "true_score" : true_score,
                "date_created": datetime.now()
            }
            for article in article_list:
                index = str(article_list.index(article))
                insert_dict["Article" + index] = {
                    "url" : article.url,
                    "title" : article.title,
                    "full_article" : article.full_article,
                    "summarized_article" : article.summarized_article,
                    "similarity_score" : article.similarity_score
                }

            result_DA = mongo.db.result_DA
            result_DA.insert_one(insert_dict)

            '''
            print(insert_dict)
            print(f"input_text: {input_text}")
            print(f"search_term: {search_term}")
            print(f"true_score: {true_score}")
            for article in article_list:
                article.get()
            '''
            flash("Disinformation Analysis successfully added to Database", "success")

        except Exception as e:
            print(f"POST Error! - {e}")

        finally:
            return redirect('/')
    else:
        return render_template('disinformation.html')

if __name__ == "__main__":
    app.run(debug=True)