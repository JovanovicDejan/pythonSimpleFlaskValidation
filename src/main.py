from flask import Flask,render_template,request,session,redirect,url_for
import mysql.connector
app = Flask(__name__)
app.config['SECRET_KEY'] = "RAF2021-2022"
mydb = mysql.connector.connect(
	host="localhost",
	user="root",
	password="", 
	database="test_db"
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
# 	Pravimo sql upit pomocu kog upisujemo podatke u bazu podataka (MYSQL)
	sql_statement = "INSERT INTO korisnik VALUES(null,?,?,?,?,?,?)"
# 	Kao parametre za bazu koristimo podatke koje je korisnik uneo u input polja, koja se nalaze u html-u
	parameters = (broj_indeksa,ime_prezime,godina_rodjenja,password,prosek,broj_polozenih_ispita)
# 	Izvrsavamo komandu sql, zajedno sa parametrima
	cursor.execute(sql_statement,parameters)
# 	Kada nesto radimo sa bazom podataka potrebno je da commitujemo promene odnosno da "sacuvamo"
	mydb.commit()

# 	Kada korisnik zavrsi sa registracijom redirektujemo ga na stranicu show_all
	return redirect(url_for('show_all'))


# Ruta login ima post i get metode
@app.route('/login', methods=["POST","GET"])
def login():
# 	Proveravamo da li je korisnik u sesiji, ako jeste redirektujemo ga na show_all stranicu
	if 'user' in session:
		return redirect(url_for('show_all'))
# 	Proveravamo da li je metoda get ako jeste renderujemo template login.html
	if request.method == "GET":
		return render_template(
			'login.html'
		)
	
# 	Postavljamo cursor na prepared=True
	cursor = mydb.cursor(prepared=True)
# 	iz input polja kupimo potrebne podatke
	broj_indeksa = request.form['broj_indeksa']
	password = request.form['password']
# 	Pravimo sql upit
	sql_statement = "SELECT * FROM korisnik WHERE broj_indeksa=?"
# 	Kao parametar koristimo neku vrednost iz inputa da bi proverili da li uopste taj korisnik postoji u bazi
	parameters = (broj_indeksa,)
	cursor.execute(sql_statement,parameters)
# 	Radimo fetchone da bi proverili da li postoji poklapanje sa jedinom korisnikom
	check = cursor.fetchone()
# 	Ako ne postoji vracamo gresku i ostavljamo korisnika na stranici login.html
	if check == None:
		return render_template(
			'login.html',
			broj_indeksa_error = "Ovaj broj indeksa ne postoji"
		)
	
# 	Proveravmo password, koristimo promenjivu u koju smo sacuvali fetchone, i iz nje izvlacimo 4 podatak iz liste, odnosno u nasem slucaju password iz baze
	if password != str(check[4].decode()):
		return render_template(
			'login.html',
			password_error = "Sifre se ne poklapaju"
		)
	
# 	Ako sve prodje kako treba otvaramo sesiju i cuvamo neku vrednost u sesiji
	session['user'] = broj_indeksa
# 	Redirektujemo korisnika na stranicu show_all
	return redirect(url_for('show_all'))

# Pravimo rutu logout
@app.route('/logout')
def logout():
# 	Ako korisnik nije u sesiji
	if 'user' not in session:
# 		redirektujemo ga na stranicu show_all
		return redirect(url_for('show_all'))
# Ako jeste onda ga "izbacujemo" iz sesije
	session.pop('user')
# 	redirektujemo ga na stranicu login
	return redirect(url_for('login'))


# Pravimo update rutu koja ima post i get metodu, kao parametar uzimamo neku vrendost iz base po kome cemo dohvatati korisnika kog updatujemo
@app.route('/update/<broj_indeksa>', methods=["POST","GET"])
def update(broj_indeksa):

	cursor = mydb.cursor(prepared=True)
# 	Prvo proveravmo da li postoji taj korisnik
	sql_statement = "SELECT * FROM korisnik WHERE broj_indeksa=?"
	parameters = (broj_indeksa,)
	cursor.execute(sql_statement,parameters
		       
#	Pomocu fetchone dohvatamo zeljenog korisnika iz baze
	check = cursor.fetchone()
	
# 	Posto se u bazi nalaze podaci tipa bytearray, nepohdno ih je decodovati u citljiv format, prebacujemo podatke koje smo dohvatili u listu da bi lakse mogli da radimo sa njima
	check = list(check)
	n = len(check)
# 	Za svako i u opsegu n
	for i in range(n):
# 		       Proveravmo da li je istanca(rezultata fetchone , bytearray)
		if isinstance(check[i], bytearray):
# 		       Ako jeste decodujemo ga
			check[i] = check[i].decode()

# 	Ako je metoda kojom pristupamo get, ispisujemo zeljenje podatke na stranicu koje dohvatamo iz baze da bi korisnik imao vec svoje podatke tu
	if request.method == "GET":
		return render_template(
			'update.html',
			write = check
		)
# 	Pripremamo cursro na true
	cursor = mydb.cursor(prepared=True)
# 	Iz forme u html-u dohvatamo input vrednosti
	ime_prezime = request.form['ime_prezime']
	godina_rodjenja = request.form['godina_rodjenja']
	password = request.form['password']
	confirm_password = request.form['confirm_password']
	prosek = request.form['prosek']
	broj_polozenih_ispita = request.form['broj_polozenih_ispita']
# 	Vrsimo provere koje zelimo
	if password != confirm_password:
		return render_template(
			'update.html',
			write = check,
			password_error = "Sifre se ne poklapaju"
		)
# 	pomocu int(vrednost) pretvarmo u podatak tipa intiger
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

# 	Pravimo sql upit sa UPDATE metodom koja kao argumente prima sve podatke koje menjamo
	sql_statement = "UPDATE korisnik SET ime_prezime=?,godina_rodjenja=?,sifra=?,prosek=?,polozeni_ispiti=? WHERE broj_indeksa=?"
# 	Dohvatamo iz input polja sve vrednosti koje upisujemo u bazu podataka
	parameters = (ime_prezime,godina_rodjenja,password,prosek,broj_polozenih_ispita,broj_indeksa)
	cursor.execute(sql_statement,parameters)
	mydb.commit()
#	Redirektujemo korisnika na stranicu koju zelimo
	return redirect(url_for('show_all'))

# 	Pravimo rutu za delet 
@app.route('/delete/<broj_indeksa>', methods=["POST"])
def delete(broj_indeksa):
# 	Proveravmo da li je  korisnik u sesiji
	if 'user' not in session:
# 		       Ako nije redirektujemo ga na stranicu login
		return redirect(url_for('login'))
	
# 	pravimo upit za Delete
	cursor = mydb.cursor(prepared=True)
	sql_statement = "DELETE FROM korisnik WHERE broj_indeksa=?"
	parameters = (broj_indeksa,)
	cursor.execute(sql_statement,parameters)
	mydb.commit()
	return redirect(url_for('show_all'))

		       
# Pravimo rutu show_all
@app.route('/show_all')
def show_all():
	cursor = mydb.cursor(prepared=True)
# 	Pravimo upit za dohvatanje svih vrednsot iz zeljenje tabele
	sql_statement = "SELECT * FROM korisnik"
	cursor.execute(sql_statement)
# 	pomocu fetchall dohvatamo sve podatke
	check = cursor.fetchall()
# 	Proveravmo da li postoji neki korisnik u tabeli
	if check == None:
		return "Trenutno ne postoji nijedan korisnik u bazi"
# 	Posto fetchall kao rezultat vraca tupple objekat moramo da dohvatimo njegovu duzinu i duzinu koja je bytearray
# 	Pomocu for petlje prolazimo prvo korz sve tupple vrednosti pa korz bytearray vrednosti, u kojoj vrsimo decodovanje
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

		       
		       
# 	Pravimo rutu bolji od proseka kojoj kao paramaetar prima neku vrednost koju je potrebno iskoristit u sql upitu
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
