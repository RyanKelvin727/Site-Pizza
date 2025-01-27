from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Configurações do banco de dados e do upload de arquivos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///produtos.db'  # Banco de dados SQLite local
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = '/static/uploads'  # Pasta para armazenar as imagens
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Inicializando o banco de dados
db = SQLAlchemy(app)

# Modelo Produto
class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(300), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    imagem = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'<Produto {self.nome}>'

# Criando o banco de dados (apenas uma vez, se necessário)
with app.app_context():
    db.create_all()

# Função para verificar o tipo de arquivo
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Rota para a página principal
@app.route('/')
def home():
    # Buscando todos os produtos para exibir
    produtos = Produto.query.all()
    return render_template('index.html', produtos=produtos)

# Rota para a página CRUD (criação, edição, deleção)
@app.route('/crud', methods=['GET', 'POST'])
def crud():
    # Verificando se a pasta de uploads existe, senão cria
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        preco = float(request.form['preco'])

        imagem = request.files['imagem']
        if imagem and allowed_file(imagem.filename):
            filename = secure_filename(imagem.filename)
            imagem.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            imagem_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        else:
            imagem_url = None

        produto_id = request.form.get('produto_id')
        if produto_id:  # Caso seja edição
            produto = Produto.query.get(produto_id)
            produto.nome = nome
            produto.descricao = descricao
            produto.preco = preco
            produto.imagem = imagem_url if imagem_url else produto.imagem
            db.session.commit()
        else:  # Caso seja criação
            novo_produto = Produto(nome=nome, descricao=descricao, preco=preco, imagem=imagem_url)
            db.session.add(novo_produto)
            db.session.commit()

        return redirect(url_for('home'))

    return render_template('crud.html')

# Rota para editar um produto
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    produto = Produto.query.get_or_404(id)
    if request.method == 'POST':
        produto.nome = request.form['nome']
        produto.descricao = request.form['descricao']
        produto.preco = float(request.form['preco'])
        
        imagem = request.files['imagem']
        if imagem and allowed_file(imagem.filename):
            filename = secure_filename(imagem.filename)
            imagem.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            produto.imagem = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        db.session.commit()
        return redirect(url_for('home'))
    
    return render_template('editar.html', produto=produto)

# Rota para deletar um produto
@app.route('/deletar/<int:id>', methods=['GET'])
def deletar(id):
    produto = Produto.query.get_or_404(id)
    db.session.delete(produto)
    db.session.commit()
    return redirect(url_for('home'))

# Rota para listar produtos
@app.route('/listar')
def listar():
    produtos = Produto.query.all()
    return render_template('listar.html', produtos=produtos)

if __name__ == '__main__':
    app.run(debug=True)
