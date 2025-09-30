from flask import Flask, render_template, request, redirect, url_for
from datetime import date
import sqlite3

app = Flask(__name__)

# Lista fixa de tarefas
tarefas = [
    "Cozinha Cima",
    "Cozinha baixo + escadas",
    "Banheiro baixo + salinha",
    "Sala + Entrada",
    "Banheiro cima",
    "Organizar área da stella e limpar varanda",
    "Área de baixo + Corredor máquina",
    "Limpeza da dispensa",
    "Folga",
    "Folga"
]

# Lista inicial de responsáveis
responsaveis_base = [
    "Duposto", "Jubileu", "Vigarista", "Peçarrara", "Karcaça",
    "Macalé", "Serrote", "6bomba", "Falamansa", "Parabrisas"
]

# ---------- BANCO DE DADOS ----------
def init_db():
    conn = sqlite3.connect("tarefas.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            semana INTEGER,
            ano INTEGER,
            tarefa TEXT,
            responsavel TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

def registrar_tarefas(semana, ano, tabela):
    conn = sqlite3.connect("tarefas.db")
    cur = conn.cursor()
    for _, tarefa, responsavel in tabela:
        cur.execute("INSERT INTO historico (semana, ano, tarefa, responsavel, status) VALUES (?, ?, ?, ?, ?)",
                    (semana, ano, tarefa, responsavel, "pendente"))
    conn.commit()
    conn.close()

def buscar_tarefas(semana, ano):
    conn = sqlite3.connect("tarefas.db")
    cur = conn.cursor()
    cur.execute("SELECT id, tarefa, responsavel, status FROM historico WHERE semana=? AND ano=?", (semana, ano))
    rows = cur.fetchall()
    conn.close()
    return rows

def atualizar_status(id_tarefa, status):
    conn = sqlite3.connect("tarefas.db")
    cur = conn.cursor()
    cur.execute("UPDATE historico SET status=? WHERE id=?", (status, id_tarefa))
    conn.commit()
    conn.close()

def buscar_historico():
    conn = sqlite3.connect("tarefas.db")
    cur = conn.cursor()
    cur.execute("SELECT semana, ano, tarefa, responsavel, status FROM historico ORDER BY ano DESC, semana DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

# ---------- FUNÇÃO ESCALA ----------
def escala_atual():
    hoje = date.today()
    semana = hoje.isocalendar()[1]
    ano = hoje.isocalendar()[0]

    rotacao = (semana*2) % len(responsaveis_base)
    responsaveis = responsaveis_base[rotacao:] + responsaveis_base[:rotacao]
    

    tabela = list(zip(range(1, len(tarefas)+1), tarefas, responsaveis))

    # Checar se já existe registro no banco, senão registrar
    if not buscar_tarefas(semana, ano):
        registrar_tarefas(semana, ano, tabela)

    return semana, ano, buscar_tarefas(semana, ano)

# ---------- ROTAS ----------
@app.route("/")
def index():
    semana, ano, tabela = escala_atual()
    return render_template("index.html", tabela=tabela, semana=semana, ano=ano)

@app.route("/fazer/<int:id_tarefa>")
def fazer(id_tarefa):
    atualizar_status(id_tarefa, "feita")
    return redirect(url_for("index"))

@app.route("/historico")
def historico():
    dados = buscar_historico()
    return render_template("historico.html", dados=dados)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
    port = int(os.environ.get("PORT", 5000))  # pega a porta do Railway, ou usa 5000 local
    app.run(host="0.0.0.0", port=port, debug=True)