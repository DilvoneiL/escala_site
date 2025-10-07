from flask import Flask, render_template, request, redirect, url_for
from datetime import date, timedelta
import sqlite3
import os

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
    "Parabrisas", "Falamansa", "Jubileu", "Duposto", "Peçarrara", 
    "Vigarista", "Macalé", "Karcaça", "6bomba", "Serrote"
]

# Define o gatilho dinamicamente, baseado na penúltima dupla da lista original.
# Isso torna a lógica flexível a qualquer mudança de nomes.
GATILHO_DO_CICLO = set(responsaveis_base[-4:-2])


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

# ---------- FUNÇÃO ESCALA (COM GATILHO DINÂMICO) ----------
def escala_atual():
    global responsaveis_base

    hoje = date.today()
    data_ajustada = hoje - timedelta(days=2) 
    semana = data_ajustada.isocalendar()[1]
    ano = data_ajustada.isocalendar()[0]

    rotacao = (semana * -2) % len(responsaveis_base)
    responsaveis = responsaveis_base[rotacao:] + responsaveis_base[:rotacao]

    pessoas_de_folga = set(responsaveis[-2:])
    
    # Usa a variável GATILHO_DO_CICLO em vez de nomes fixos
    if pessoas_de_folga == GATILHO_DO_CICLO:
        
        print(f"--- CICLO COMPLETO! GATILHO ATINGIDO COM: {GATILHO_DO_CICLO}. INVERTENDO AS DUPLAS ---")
        
        nova_lista_base = responsaveis_base[:]
        for i in range(0, len(nova_lista_base) - 1, 2):
            nova_lista_base[i], nova_lista_base[i+1] = nova_lista_base[i+1], nova_lista_base[i]

        responsaveis_base = nova_lista_base
        print(f"Nova ordem da lista base: {responsaveis_base}")

        responsaveis = responsaveis_base[rotacao:] + responsaveis_base[:rotacao]

    tabela = list(zip(range(1, len(tarefas)+1), tarefas, responsaveis))

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

# Bloco de execução corrigido
if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)