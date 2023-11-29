import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from settings import config, SECRET_KEY


app = Flask(__name__)
app.config.from_object('settings')
app.secret_key = SECRET_KEY

def get_db_connection():
    connection = mysql.connector.connect(**config)
    return connection

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/testdb')
def testdb():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(tables=tables), 200
    except mysql.connector.Error as err:
        app.logger.error(f"Erro ao conectar ao banco de dados: {err}")
        return jsonify(message="Erro ao conectar ao banco de dados.", error=str(err)), 500

def create_database_if_not_exists():
    host = 'localhost'
    user = 'root'
    password = '1234'
    connection = mysql.connector.connect(host=host, user=user, password=password)
    cursor = connection.cursor()
    database_name = 'aula_13_10'
    cursor.execute(f"SHOW DATABASES LIKE '{database_name}'")
    result = cursor.fetchone()
    if result is None:
        cursor.execute(f"CREATE DATABASE {database_name}")
        print(f"Banco de dados `{database_name}` criado com sucesso!")
    else:
        print(f"Banco de dados `{database_name}` já existe.")
    cursor.close()
    connection.close()

def get_db_connection():
    create_database_if_not_exists()
    host = 'localhost'
    database = 'aula_13_10'
    user = 'root'
    password = '1234'
    connection = mysql.connector.connect(
        host=host,
        database=database,
        user=user,
        password=password
    )
    return connection

@app.route('/novo_setor')
def novo_setor():
    return render_template('setor_form.html')

@app.route('/novo_funcionario')
def novo_funcionario():
    setores = []
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id, nome FROM setor")
        setores = cursor.fetchall()
        
    except mysql.connector.Error as err:
        print("Erro ao ler os dados do setor: ", err)
    finally:
        cursor.close()
        connection.close()
    return render_template('funcionario_form.html', setores=setores)

@app.route('/criar_funcionario', methods=['POST'])
def criar_funcionario():
    primeiro_nome = request.form['primeiro_nome']
    sobrenome = request.form['sobrenome']
    data_admissao = request.form['data_admissao']
    status_funcionario = 'status_funcionario' in request.form
    id_setor = request.form['id_setor']
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = """
        INSERT INTO funcionarios (primeiro_nome, sobrenome, data_admissao, status_funcionario, id_setor) 
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (primeiro_nome, sobrenome, data_admissao, status_funcionario, id_setor))
        connection.commit()
        flash('Funcionário criado com sucesso!', 'success')
    except mysql.connector.Error as err:
        flash(f'Erro ao criar o funcionário: {err}', 'error')
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return redirect(url_for('funcionarios'))

@app.route('/funcionario_criado')
def funcionario_criado():
    return "Funcionário criado com sucesso!"

@app.route('/criar_setor', methods=['POST'])
def criar_setor():
    nome_setor = request.form['nome']

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = "INSERT INTO setor (nome) VALUES (%s)"
        cursor.execute(query, (nome_setor,))
        connection.commit() 
        flash('Setor criado com sucesso!', 'success')  
    except mysql.connector.Error as err:
        flash(f'Erro ao criar o setor: {err}', 'error')
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return redirect(url_for('setores'))

@app.route('/setor_criado')
def setor_criado():
    return "Setor criado com sucesso!"

@app.route('/novo_cargo')
def novo_cargo():
    setores = []
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id, nome FROM setor")
        setores = cursor.fetchall()
    except mysql.connector.Error as err:
        print("Erro ao ler os dados do setor: ", err)
    finally:
        cursor.close()
        connection.close()

    return render_template('cargo_form.html', setores=setores)

@app.route('/criar_cargo', methods=['POST'])
def criar_cargo():
    nome = request.form['nome']
    id_setor = request.form['id_setor']

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO cargos (nome, id_setor) VALUES (%s, %s)", (nome, id_setor))
        connection.commit()
        flash('Cargo criado com sucesso!', 'success')
    except mysql.connector.Error as err:
        flash(f'Erro ao criar o cargo: {err}', 'error')
    finally:
        cursor.close()
        connection.close()
    return redirect(url_for('cargos'))

@app.route('/cargo_criado')
def cargo_criado():
    return "Cargo criado com sucesso!"

@app.route('/setores')
def setores():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, nome FROM setor")
    setores = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('setores.html', setores=setores)

@app.route('/funcionarios')
def funcionarios():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, primeiro_nome, sobrenome FROM funcionarios")
    funcionarios = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('funcionarios.html', funcionarios=funcionarios)

@app.route('/cargos')
def cargos():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, nome FROM cargos")
    cargos = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('cargos.html', cargos=cargos)

def create_tables_if_not_exists():
    connection = get_db_connection()
    cursor = connection.cursor()
    create_table_setor = """
    CREATE TABLE IF NOT EXISTS setor (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(50) NOT NULL
    );
    """
    create_table_funcionarios = """
    CREATE TABLE IF NOT EXISTS funcionarios (
        id INT AUTO_INCREMENT PRIMARY KEY,
        primeiro_nome VARCHAR(50) NOT NULL,
        sobrenome VARCHAR(50) NOT NULL,
        data_admissao DATE NOT NULL,
        status_funcionario BOOL NOT NULL,
        id_setor INT,
        FOREIGN KEY (id_setor) REFERENCES setor(id)
    );
    """
    create_table_cargos = """
    CREATE TABLE IF NOT EXISTS cargos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(50),
        id_setor INT,
        FOREIGN KEY (id_setor) REFERENCES setor(id)
    );
    """

    cursor.execute(create_table_setor)
    cursor.execute(create_table_funcionarios)
    cursor.execute(create_table_cargos)

    cursor.close()
    connection.commit()
    connection.close()

create_tables_if_not_exists()

if __name__ == '__main__':
    app.run(debug=True)
