from flask import Flask,render_template,request,session,redirect,url_for
import mysql.connector
app = Flask(__name__)
app.config['SECRET_KEY'] = "RAF2021-2022"
mydb = mysql.connector.connect(
	host="localhost",
	user="root",
	password="", 
    
	database="kolokvijum_python" # napraviti bazu i importovati
    # korisnik.sql u nju 
    )

@app.route('/')
def index():
    return 'Hello world'

# Pravimo rutu register koja ima metode post i get
@app.route('/register', methods=["POST","GET"])
def register():
	# Ako korisnik pristupa stranici prikazujemo register.html
	if request.method == "GET":
		return  render_template(
			'register.html'
		)
	
	cursor = mydb.cursor(prepared=True)
	# Iz input polja iz forme kupimo vrednosti koje dohvatamo pomocu taga name u html-u
	broj_indeksa = request.form['broj_indeksa']
	ime_prezime = request.form['ime_prezime']
	godina_rodjenja = request.form['godina_rodjenja']
	password = request.form['password']
	confirm_password = request.form['confirm_password']
	prosek = request.form['prosek']
	broj_polozenih_ispita = request.form['broj_polozenih_ispita']
	# Pravimo sql upit gde dohvatamo sve iz tabele korisnik gde je broj indeksa onaj koji je korisnik uneo u input polje
	sql_statement = "SELECT * FROM korisnik WHERE broj_indeksa=?"
	parameters = (broj_indeksa,)
	cursor.execute(sql_statement,parameters)
	# Pravimo promenjivu za proveru u bazi
	check = cursor.fetchone()
	
	# Ako je razlicito od None to znaci da su se vrednosti poklopile vracamo gresku
	if check != None:
		return render_template(
			'register.html',
			broj_indeksa_error = "Ovaj broj indeksa vec postoji pokusajte ponovo"
		)
	
	if password != confirm_password:
		return render_template(
			'register.html',
			password_error = "Sifre se ne poklapaju"
		)
	
	prosek = float(prosek)
	if prosek > 10 or prosek < 6:
		return render_template(
			'register.html',
			prosek_error = "Prosek mora ne sme biti ispod  6 i iznad 10"
		)
	

	broj_polozenih_ispita = int(broj_polozenih_ispita)
	if broj_polozenih_ispita < 0:
		return render_template(
			'register.html',
			broj_polozenih_ispita_error = "Broj polozenih ispita ne sme biti manji od 0"
		)
	
	cursor = mydb.cursor(prepared=True)
	sql_statement = "INSERT INTO korisnik VALUES(null,?,?,?,?,?,?)"
	parameters = (broj_indeksa,ime_prezime,godina_rodjenja,password,prosek,broj_polozenih_ispita)
	cursor.execute(sql_statement,parameters)
	mydb.commit()

	return redirect(url_for('show_all'))


@app.route('/login', methods=["POST","GET"])
def login():
	if 'user' in session:
		return redirect(url_for('show_all'))
	if request.method == "GET":
		return render_template(
			'login.html'
		)
	
	cursor = mydb.cursor(prepared=True)
	broj_indeksa = request.form['broj_indeksa']
	password = request.form['password']
	sql_statement = "SELECT * FROM korisnik WHERE broj_indeksa=?"
	parameters = (broj_indeksa,)
	cursor.execute(sql_statement,parameters)
	check = cursor.fetchone()
	if check == None:
		return render_template(
			'login.html',
			broj_indeksa_error = "Ovaj broj indeksa ne postoji"
		)
	
	if password != str(check[4].decode()):
		return render_template(
			'login.html',
			password_error = "Sifre se ne poklapaju"
		)
	
	session['user'] = broj_indeksa
	return redirect(url_for('show_all'))

@app.route('/logout')
def logout():
	if 'user' not in session:
		return redirect(url_for('show_all'))
	session.pop('user')
	return redirect(url_for('login'))


@app.route('/update/<broj_indeksa>', methods=["POST","GET"])
def update(broj_indeksa):

	cursor = mydb.cursor(prepared=True)
	sql_statement = "SELECT * FROM korisnik WHERE broj_indeksa=?"
	parameters = (broj_indeksa,)
	cursor.execute(sql_statement,parameters)
	check = cursor.fetchone()
	check = list(check)
	n = len(check)
	for i in range(n):
		if isinstance(check[i], bytearray):
			check[i] = check[i].decode()


	if request.method == "GET":
		return render_template(
			'update.html',
			write = check
		)
	
	cursor = mydb.cursor(prepared=True)
	ime_prezime = request.form['ime_prezime']
	godina_rodjenja = request.form['godina_rodjenja']
	password = request.form['password']
	confirm_password = request.form['confirm_password']
	prosek = request.form['prosek']
	broj_polozenih_ispita = request.form['broj_polozenih_ispita']
	if password != confirm_password:
		return render_template(
			'update.html',
			write = check,
			password_error = "Sifre se ne poklapaju"
		)
	
	prosek = int(prosek)
	if prosek < 6 and prosek > 10:
		return render_template(
			'update.html',
			write = check,
			prosek_error = "Ne sme biti manji od 6 a veci od 10"
		)
	
	broj_polozenih_ispita = int(broj_polozenih_ispita)
	if broj_polozenih_ispita < 0:
		return render_template(
			'update.html',
			write = check,
			broj_polozenih_ispita_error = "Ne sme biti negativan broj"
		)
	sql_statement = "UPDATE korisnik SET ime_prezime=?,godina_rodjenja=?,sifra=?,prosek=?,polozeni_ispiti=? WHERE broj_indeksa=?"
	parameters = (ime_prezime,godina_rodjenja,password,prosek,broj_polozenih_ispita,broj_indeksa)
	cursor.execute(sql_statement,parameters)
	mydb.commit()
	return redirect(url_for('show_all'))

@app.route('/delete/<broj_indeksa>', methods=["POST"])
def delete(broj_indeksa):
	if 'user' not in session:
		return redirect(url_for('login'))
	
	cursor = mydb.cursor(prepared=True)
	sql_statement = "DELETE FROM korisnik WHERE broj_indeksa=?"
	parameters = (broj_indeksa,)
	cursor.execute(sql_statement,parameters)
	mydb.commit()
	return redirect(url_for('show_all'))

@app.route('/show_all')
def show_all():
	cursor = mydb.cursor(prepared=True)
	sql_statement = "SELECT * FROM korisnik"
	cursor.execute(sql_statement)
	check = cursor.fetchall()
	if check == None:
		return "Trenutno ne postoji nijedan korisnik u bazi"
	
	n = len(check)
	m = len(check[0])
	for i in range(n):
		check[i] = list(check[i])
		for j in range(m):
			if isinstance(check[i][j], bytearray):
				check[i][j] = check[i][j].decode()
	
	return render_template(
		'show_all.html',
		users = check
	)

@app.route('/better_than_average/<average>')
def better_than_average(average):
	cursor = mydb.cursor(prepared=True)
	sql_statement = "SELECT * FROM korisnik WHERE prosek>=?"
	parameters = (average,)
	cursor.execute(sql_statement,parameters)
	check = cursor.fetchall()

	if check == None:
		return "Ne postoji nijedan korisnik  koji ima prosek veci od tog"
	
	n = len(check)
	m = len(check[0])
	for i in range(n):
		check[i] = list(check[i])
		for j in range(m):
			if isinstance(check[i][j], bytearray):
				check[i][j] = check[i][j].decode()
	
	return render_template(
		'better_than_average.html',
		data = check
	)


app.run(debug=True)
