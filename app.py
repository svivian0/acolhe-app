from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import re # Importa o módulo de expressões regulares

app = Flask(__name__)

# --- Configuração do Banco de Dados ---
# Configuração para MySQL (WAMP)
# Formato: 'mysql+pymysql://usuario:senha@servidor/nome_do_banco'
# Crie um banco de dados chamado 'acolhe_app_db' no seu phpMyAdmin.
# Por padrão, o usuário do WAMP é 'root' e a senha é vazia. Ajustado para 'acolheapp'.
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/acolheapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Desativa avisos desnecessários
app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-forte' # Necessário para usar 'flash'

# Inicializa a extensão SQLAlchemy com o nosso app Flask
db = SQLAlchemy(app)

# --- Configuração do Flask-Login ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Rota para redirecionar se o usuário não estiver logado
login_manager.login_message = "Por favor, faça login para acessar esta página."
login_manager.login_message_category = "info"


# --- Modelos (Tabelas do Banco de Dados) ---
class Usuario(db.Model, UserMixin): # Herda de UserMixin
    __tablename__ = 'usuarios'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    tipo_usuario = db.Column(db.String(50), nullable=False) # SQLAlchemy trata ENUM como String
    criado_em = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    # Método necessário para o Flask-Login
    def get_id(self):
        return self.id_usuario

class PerfilPessoal(db.Model):
    __tablename__ = 'perfis_pessoais'
    id_perfil_pessoal = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), unique=True, nullable=False)
    neurodivergencia = db.Column(db.String(255))
    sobremim = db.Column(db.String(200))
    imagemperfil = db.Column(db.String(200))
    usuario = db.relationship('Usuario', backref=db.backref('perfil_pessoal', uselist=False))

class Estabelecimento(db.Model):
    __tablename__ = 'estabelecimentos'
    id_estabelecimento = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    razao_social = db.Column(db.String(255), nullable=False)
    cnpj = db.Column(db.String(18), unique=True, nullable=False)
    endereco = db.Column(db.Text, nullable=False)
    telefone = db.Column(db.String(20))
    descricao = db.Column(db.Text)
    imagemperfilestab = db.Column(db.String(200))
    media_avaliacao = db.Column(db.Numeric(2, 1), default=0.0)
    usuario = db.relationship('Usuario', backref=db.backref('estabelecimento', uselist=False))

class Categoria(db.Model):
    __tablename__ = 'categorias'
    id_categoria = db.Column(db.Integer, primary_key=True)
    nome_categoria = db.Column(db.String(100), unique=True, nullable=False)

class EstabelecimentoCategoria(db.Model):
    __tablename__ = 'estabelecimento_categoria'
    id_estabelecimento_categoria = db.Column(db.Integer, primary_key=True)
    id_estabelecimento = db.Column(db.Integer, db.ForeignKey('estabelecimentos.id_estabelecimento'), nullable=False)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id_categoria'), nullable=False)

class Acessibilidade(db.Model):
    __tablename__ = 'acessibilidade'
    id_acessibilidade = db.Column(db.Integer, primary_key=True)
    item_acessibilidade = db.Column(db.String(255), unique=True, nullable=False)

class EstabelecimentoAcessibilidade(db.Model):
    __tablename__ = 'estabelecimento_acessibilidade'
    id_estabelecimento_acessibilidade = db.Column(db.Integer, primary_key=True)
    id_estabelecimento = db.Column(db.Integer, db.ForeignKey('estabelecimentos.id_estabelecimento'), nullable=False)
    id_acessibilidade = db.Column(db.Integer, db.ForeignKey('acessibilidade.id_acessibilidade'), nullable=False)

class Avaliacao(db.Model):
    __tablename__ = 'avaliacoes'
    id_avaliacao = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    id_estabelecimento = db.Column(db.Integer, db.ForeignKey('estabelecimentos.id_estabelecimento'), nullable=False)
    nota_geral = db.Column(db.Numeric(2, 1), nullable=False)
    comentario = db.Column(db.Text)
    data_avaliacao = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    # Relacionamentos para facilitar o acesso aos objetos
    usuario = db.relationship('Usuario', backref='avaliacoes')
    estabelecimento = db.relationship('Estabelecimento', backref='avaliacoes')

    # Adicionando a restrição de verificação (CHECK) no nível do modelo, se necessário
    __table_args__ = (
        db.CheckConstraint('nota_geral BETWEEN 1.0 AND 5.0', name='check_nota_geral_range'),
        db.UniqueConstraint('id_usuario', 'id_estabelecimento', name='uq_usuario_estabelecimento_avaliacao')
    )

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# --- Rotas da Aplicação ---
@app.route('/')
def Rota_html():
    # A rota principal agora redireciona para a tela de login
    return redirect(url_for('login'))

@app.route('/home')
@login_required # Protege a rota, só permite acesso se o usuário estiver logado
def home():
    return render_template('acolhe_app_home.html', titulo="Acolhe App", usuario=current_user)

# Rota para a página de Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        # Tratamento de erro: verifica se os campos não estão vazios
        if not email or not senha:
            flash('Todos os campos são obrigatórios.', 'danger')
            return redirect(url_for('login'))

        # Busca o usuário pelo email
        usuario = Usuario.query.filter_by(email=email).first()

        # Verifica se o usuário existe e se a senha está correta
        if usuario and check_password_hash(usuario.senha, senha):
            # Se a senha estiver correta, registra o usuário na sessão
            login_user(usuario)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('home')) # Redireciona para a página home
        else:
            flash('Email ou senha inválidos. Tente novamente.', 'danger')

    return render_template('login.html', titulo="Login")

# Rota para Logout
@app.route('/logout')
def logout():
    logout_user()
    flash('Você foi desconectado.', 'success')
    return redirect(url_for('login'))

# Rota para a página de Cadastro
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro_html():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        tipo_usuario = request.form.get('tipo_usuario')

        # Tratamento de erro: verifica se todos os campos foram preenchidos
        if not nome or not email or not senha or not tipo_usuario:
            flash('Todos os campos são obrigatórios.', 'danger')
            return redirect(url_for('cadastro_html'))

        # Verifica se o email já existe
        if Usuario.query.filter_by(email=email).first():
            flash('Este email já está cadastrado. Tente fazer login.', 'warning')
            return redirect(url_for('cadastro_html'))

        # Cria o hash da senha para não salvá-la em texto puro e cria o usuário base
        senha_hashed = generate_password_hash(senha, method='pbkdf2:sha256')
        novo_usuario = Usuario(nome=nome, email=email, senha=senha_hashed, tipo_usuario=tipo_usuario)
        db.session.add(novo_usuario)

        # Se for uma conta empresarial, coleta os dados e cria o estabelecimento
        if tipo_usuario == 'empresarial':
            razao_social = request.form.get('razao_social')
            cnpj_bruto = request.form.get('cnpj')
            endereco = request.form.get('endereco')

            if not razao_social or not cnpj_bruto or not endereco:
                flash('Para contas empresariais, Razão Social, CNPJ e Endereço são obrigatórios.', 'danger')
                return redirect(url_for('cadastro_html'))

            # --- FILTRO DO CNPJ ---
            # Remove todos os caracteres que não são dígitos
            cnpj_limpo = re.sub(r'[^\d]', '', cnpj_bruto)

            # Verifica se o CNPJ limpo já existe no banco
            if Estabelecimento.query.filter_by(cnpj=cnpj_limpo).first():
                flash('Este CNPJ já está cadastrado.', 'warning')
                return redirect(url_for('cadastro_html'))

            # Garante que o usuário seja salvo primeiro para obter o ID
            db.session.flush()

            novo_estabelecimento = Estabelecimento(
                id_usuario=novo_usuario.id_usuario,
                nome=nome, # Usando o 'nome' do formulário como nome fantasia
                email=email,
                senha=senha_hashed, # Armazenando a senha hashada também aqui
                razao_social=razao_social,
                cnpj=cnpj_limpo, # Salva o CNPJ limpo
                endereco=endereco
            )
            db.session.add(novo_estabelecimento)

        db.session.commit()

        # Loga o usuário recém-criado automaticamente
        login_user(novo_usuario)

        flash('Conta criada com sucesso!', 'success')
        return redirect(url_for('home')) # Redireciona direto para a página principal

    return render_template('cadastro.html', titulo="Cadastro")
    
# Rota para a página de Comércio
@app.route('/comercio')
def comercio():
    # Busca TODOS os estabelecimentos cadastrados no banco de dados.
    estabelecimentos = Estabelecimento.query.all()
    # Envia a lista de estabelecimentos para o template renderizar.
    return render_template('comercio.html', titulo="Comércio", estabelecimentos=estabelecimentos)

# Rota para a página Sobre Nós
@app.route('/sobre-nos')
def sobre_nos():
    return render_template('acolhe-app-sobre-nos.html', titulo="Sobre Nós")

# Rota para a página de perfil do estabelecimento
@app.route('/perfil-estabelecimento/<int:id>')
def perfil_estabelecimento(id):
    # Busca um único estabelecimento pelo seu ID. Se não encontrar, retorna erro 404.
    estabelecimento = Estabelecimento.query.filter_by(id_estabelecimento=id).first_or_404()
    # Envia o objeto 'estabelecimento' para o template.
    return render_template('perfilestab.html', titulo=f"Perfil de {estabelecimento.nome}", estabelecimento=estabelecimento)

if __name__ == '__main__':
    app.run(debug=True)
    
