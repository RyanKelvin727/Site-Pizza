from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Configurações do banco de dados e do upload de arquivos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///produtos.db'  # Banco de dados SQLite local
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')  # Pasta para armazenar as imagens
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

# Função para verificar o tipo de arquivo
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Função para criar o banco de dados
def create_db():
    with app.app_context():
        db.create_all()

# Rota para a página principal (index.html)
@app.route('/')
def home():
    produtos = Produto.query.all()
    return render_template('index.html', produtos=produtos)

# Rota para a página CRUD (criação e edição de produtos)
@app.route('/crud', methods=['GET', 'POST'])
@app.route('/crud/<int:produto_id>', methods=['GET', 'POST'])
def crud(produto_id=None):
    if produto_id:
        produto = Produto.query.get(produto_id)  # Carrega o produto existente para editar
    else:
        produto = None

    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        preco = request.form['preco']
        imagem = request.files['imagem'] if 'imagem' in request.files else None

        if produto_id:
            # Editar produto existente
            produto.nome = nome
            produto.descricao = descricao
            produto.preco = preco
            if imagem:
                imagem_filename = imagem.filename
                imagem.save(f'static/{imagem_filename}')
                produto.imagem = imagem_filename
            db.session.commit()
        else:
            # Adicionar novo produto
            imagem_filename = None
            if imagem:
                imagem_filename = imagem.filename
                imagem.save(f'static/{imagem_filename}')
            novo_produto = Produto(nome=nome, descricao=descricao, preco=preco, imagem=imagem_filename)
            db.session.add(novo_produto)
            db.session.commit()

        return redirect(url_for('crud'))

    # Caso seja uma requisição GET, renderiza o formulário com as informações do produto
    return render_template('crud.html', produto=produto, produtos=Produto.query.all())


# Função para deletar um produto
@app.route('/deletar/<int:id>', methods=['GET'])
def deletar(id):
    produto = Produto.query.get_or_404(id)
    db.session.delete(produto)
    db.session.commit()
    return redirect(url_for('crud'))

if __name__ == '__main__':
    create_db()  # Garantir que o banco de dados seja criado ao iniciar o app
    app.run(debug=True)
