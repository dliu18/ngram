from nltk.sentiment.vader import SentimentIntensityAnalyzer
import json
import sys
from flask import Flask
from flask import request

def detect(headline, keywords):
	keyword_list = keywords.split('_')
	headline_list = headline.split(' ')

	for i in range(0, len(headline_list) - len(keyword_list) + 1):
		if headline_list[i] != keyword_list[0]:
			continue

		found_match = True
		for j in range (1, len(keyword_list)):
			if headline_list[i + j] != keyword_list[j]:
				found_match = False
				break

		if found_match:
			return True

	return False 

def save(keywords):
	print(", ".join(keywords))
	sid = SentimentIntensityAnalyzer()

	f = open("all_headlines.json", "r")

	headlines_separated_by_date = json.loads(f.read())
	year_count = {}

	most_positive = []
	most_negative = []

	length = len(keywords)

	#current code excludes last date
	for date in headlines_separated_by_date:
		try:
			headlines = headlines_separated_by_date[date]
			year = int(date[:4]) / 2

			if year not in year_count:
				year_count[year] = [0.0] * (length + 1)

			year_count[year][length] += len(headlines)

			for headline in headlines:
				#superlatives
				detected = False 
				for index in range(length):
					keyword = keywords[index]

					if detect(headline, keyword):
						detected = True 
						year_count[year][index] += 1

				if detected:
					scores = sid.polarity_scores(headline)
					positive = scores["pos"]
					negative = scores["neg"]

					most_positive.append([-1.0 * positive, date+ "\t " + headline])
					most_negative.append([-1.0 * negative, date + "\t " + headline])
		except:
			pass

	most_negative = sorted(most_negative)[0 : min(len(most_negative), 5)]
	# print "Most Negative Headlines"
	# for headline in most_negative:
	# 	try:
	# 		print headline[1], headline[0]
	# 	except:
	# 		pass
	# print "\n"

	most_positive = sorted(most_positive)[0 : min(len(most_positive), 5)]
	# print "Most Positive Headlines"
	# for headline in most_positive:
	# 	try:
	# 		print headline[1], headline[0]
	# 	except:
	# 		pass
	# print "\n"

	graphOutput = {}
	for year in year_count:
		graphOutput[year] = [count/year_count[year][length] for count in year_count[year][0:length]]


	keys = sorted(graphOutput.keys())

	y = []
	majorYears = []
	nextVal = graphOutput[keys[1]][0]
	currVal = graphOutput[keys[0]][0]
	prevVal = 0.0

	for i in range(len(keys)):
		nextVal = graphOutput[keys[min(i + 1, len(keys) - 1)]][0]
		if prevVal < 0.5 * currVal and nextVal < 0.5 * currVal:
			majorYears.append(str(2 * keys[i]))

		y.append(graphOutput[keys[i]])
		prevVal = currVal
		currVal = nextVal

	# print("Major Years")
	# print("\n".join(majorYears))

	x = [year * 2 for year in keys] 
	# plt.xlabel("Date (Year)")
	# plt.ylabel("Percentages of Headlines")
	# plt.title("Ngram Distribution of " + (", ".join(sys.argv[1:])))
	# plt.plot(x,y)
	# plt.legend()
	# plt.show() 

	return (x, y, most_negative, most_positive, majorYears)
app = Flask(__name__)

@app.route("/")
def hello():
	keywords = request.args.get('keywords', '')
	keywords = [str(x) for x in keywords.split(",")]

	resultTuple = save(keywords)
	keywords.insert(0, "Year")
	data = str(keywords) + ",\n"
	x = resultTuple[0]
	y = resultTuple[1]
	for i in range(len(x)):
		temp = [str(x[i])]
		for entry in y[i]:
			temp.append(entry)
		data += (str(temp) + ", \n")

	f = open("chart1.html", "r")
	html1 = f.read()
	f.close()

	f = open("chart2.html", "r")
	html2 = f.read()
	f.close()

	positive_table = " <div class=\"six columns\"> <h3> Most Positive Headlines </h3>"
	positive_table += "<table style=\"width: 100%\"> <tr> <th> Year </th> <th> Score </th> <th> Link </th> </tr>"
	most_positive = resultTuple[3]
	for entry in most_positive:
		score = str(-1.0 * entry[0])
		year_title = entry[1]
		year = year_title.split("\t")[0]
		title = year_title.split("\t")[1]
		link = "http://theprince.princeton.edu/princetonperiodicals/cgi-bin/princetonperiodicals?a=d&d=Princetonian" + year.strip(" ") + "-01&e=-------en-20--1--txt-txIN-------"
		positive_table += "<tr> <th>" + year[0:4] + "</th> <th>" + score + "</th> <th> <a href='" + link + "'> " + title + "</a> </th> </tr>"
	positive_table += "</table> </div>"

	negative_table = " <div class=\"six columns\"> <h3> Most Negative Headlines </h3>"
	negative_table += "<table style=\"width: 100%\"> <tr> <th> Year </th> <th> Score </th> <th> Link </th> </tr>"
	most_negative = resultTuple[2]
	for entry in most_negative:
		score = str(-1.0 * entry[0])
		year_title = entry[1]
		year = year_title.split("\t")[0]
		title = year_title.split("\t")[1]
		link = "http://theprince.princeton.edu/princetonperiodicals/cgi-bin/princetonperiodicals?a=d&d=Princetonian" + year.strip(" ") + "-01&e=-------en-20--1--txt-txIN-------"
		negative_table += "<tr> <th>" + year[0:4] + "</th> <th>" + score + "</th> <th> <a href='" + link + "'> " + title + "</a> </th> </tr>"
	negative_table += "</table> </div>"

	return html1 + data + html2 + positive_table + negative_table + "</div> </div> </body> </html>"

if __name__ == "__main__":
	app.run()

