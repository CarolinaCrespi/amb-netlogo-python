import numpy as np                       # libreria per numeri casuali e operazioni matematiche
import matplotlib.pyplot as plt          # libreria per creare grafici
import matplotlib.animation as animation # libreria per creare animazioni e salvarle come GIF
from matplotlib.patches import Patch     # serve per disegnare i rettangolini colorati nella legenda
from dataclasses import dataclass        # permette di usare @dataclass per creare classi senza scrivere __init__


# --- CONFIGURAZIONE GLOBALE ---
# Cosa fa: è lo "stampo" dei parametri del modello — raccoglie tutto in un posto solo.
# NetLogo: globals + sliders (population, beta, gamma...).
# Perché @dataclass: genera automaticamente __init__ senza doverlo scrivere a mano.
#   Si usa 'class' e non un dizionario perché si accede con cfg.beta (più leggibile di cfg['beta']).
# Come si legge: "nome_parametro: tipo = valore_default".
# Nota: population e grid_size si usano senza cfg. perché siamo ancora dentro la definizione
#   della classe — Python sa già a quale stampo appartengono.
@dataclass
class config:
    population: int = 100       # numero totale di agenti
    grid_size: int = 16         # il mondo va da -16 a +16 (patch in NetLogo)
    initial_infected: int = 10  # numero iniziale di infetti — tutti gli altri partono S
    beta: float = 0.9           # probabilità di contagio per contatto
    gamma: float = 0.05         # probabilità di guarigione per tick
    days: int = 100             # durata della simulazione in giorni

    def __post_init__(self):
        if self.initial_infected > self.population:
            raise ValueError(
                f"initial_infected ({self.initial_infected}) > population ({self.population})."
            )


# --- DEFINIZIONE DELL'AGENTE ---
# Cosa fa: descrive com'è fatto ogni singolo agente — stato SIR e posizione sulla griglia.
# NetLogo: turtle-own [ state xcor ycor ] — xcor e ycor sono interi sulle patch.
# Perché @dataclass: ogni agente è un oggetto con campi nominati. agent.pos_x è più chiaro
#   di agent[1], e si può modificare direttamente: agent.state = 'I'.
# Differenza rispetto al continuo: pos_x e pos_y sono int (celle intere), non float.
#   Rimossa velocity: nel discreto il passo è sempre 1 cella, non serve.
# pos_x e pos_y partono da 0 come default neutro — vengono assegnati davvero in crea_agenti.
@dataclass
class agent:
    state: str = 'S'   # stato dell'agente: S = Susceptible, I = Infected, R = Recovered
    pos_x: int = 0     # posizione sulla griglia (asse x) — verrà assegnata in crea_agenti
    pos_y: int = 0     # posizione sulla griglia (asse y) — verrà assegnata in crea_agenti


# --- CREAZIONE DELLA POPOLAZIONE ---
# Cosa fa: crea tutti gli agenti, li posiziona casualmente sulla griglia e assegna lo stato iniziale.
# NetLogo: setup → create-turtles N [ setxy random-pxcor random-pycor  set state ... ]
# Perché una lista: struttura più semplice per tenere insieme tutti gli agenti e iterarci sopra.
#   agents[i] è l'i-esimo agente.
# Perché a = agent() e poi a.pos_x = ...: la posizione dipende da cfg.grid_size, quindi va
#   calcolata qui dentro, non come default della classe. Si crea prima l'agente vuoto,
#   poi si assegnano i valori uno alla volta.
# Come si legge: i primi initial_infected agenti → I, i successivi initial_recovered → R, resto → S.
# return agents è obbligatorio: agents esiste solo dentro questa funzione — senza return va perso.
def crea_agenti(cfg):
    agents = []                                                         # lista vuota che conterrà tutti gli agenti
    for i in range(cfg.population):                                     # ripete per ogni agente da creare
        a = agent()                                                     # crea un agente vuoto con i default
        a.pos_x = np.random.randint(-cfg.grid_size, cfg.grid_size + 1) # assegna posizione x casuale sulla griglia
        a.pos_y = np.random.randint(-cfg.grid_size, cfg.grid_size + 1) # assegna posizione y casuale sulla griglia
        if i < cfg.initial_infected:  # i primi N agenti diventano infetti
            a.state = 'I'
        else:                         # tutti gli altri partono suscettibili
            a.state = 'S'
        agents.append(a)   # aggiunge l'agente in fondo alla lista — l'ordine non conta
    return agents          # restituisce la lista completa — senza return andrebbe persa


# --- MOVIMENTO DISCRETO ---
# Cosa fa: sposta ogni agente di 1 cella in una direzione casuale tra N, S, E, W
# DIRECTIONS è in MAIUSCOLO perché è una costante — non cambia mai durante la simulazione.
#   È una lista di tuple: le [] sono la lista, le () sono le coppie (dx, dy).
# Come funziona: randint(0,4) pesca un numero tra 0 e 3 → seleziona una tupla →
#   dx, dy = (1, 0) spacchetta la tupla in due variabili (unpacking).
# np.clip(valore, min, max): tiene l'agente dentro la griglia senza farlo uscire dai bordi.
#   Equivale a world-wrap disattivato in NetLogo.
DIRECTIONS = [(0, 1), (0, -1), (1, 0), (-1, 0)]   # N, S, E, W — costante, non cambia mai

def muovi_agenti(agents, cfg):
    for a in agents:                                                        # per ogni agente nella lista
        dx, dy = DIRECTIONS[np.random.randint(0, 4)]                       # pesca una direzione casuale e spacchetta la tupla
        a.pos_x = np.clip(a.pos_x + dx, -cfg.grid_size, cfg.grid_size)    # sposta x e blocca al bordo
        a.pos_y = np.clip(a.pos_y + dy, -cfg.grid_size, cfg.grid_size)    # sposta y e blocca al bordo


# --- CONTAGIO ---
# Cosa fa: per ogni coppia di agenti vicini (uno I e uno S), applica la probabilità beta
#   di contagio. Se il dado supera beta, l'agente S diventa I.
# NetLogo: ask turtles with [state='I'] [ ask turtles in-radius 1 with [state='S']
#            [ if random-float 1 < beta [ set state 'I' ] ] ]
# Doppio for con j > i: controlla tutte le coppie distinte senza ripetizioni né auto-contagio.
#   Con 4 agenti le coppie sono: (0,1)(0,2)(0,3)(1,2)(1,3)(2,3) — mai la stessa due volte.
# a, b = agents[i], agents[j]: solo soprannomi per leggibilità — a.state è più chiaro di agents[i].state.
# Distanza di Chebyshev: d = max(|dx|,|dy|) — cattura la cella stessa + le 8 celle vicine.
#   Salvata in d (non solo True/False) così può essere riusata in futuro (es. scalare beta).
#   Se d > 1 gli agenti sono lontani → continue salta direttamente alla coppia successiva.
# np.random.rand(): genera un numero casuale tra 0 e 1. Se è minore di beta (es. 0.3)
#   il contagio avviene — più alto è beta, più probabile è il contagio.
def contagio(agents, cfg):
    for i in range(len(agents)):            # scorre tutti gli agenti
        for j in range(i + 1, len(agents)): # scorre solo le coppie non ancora controllate
            a, b = agents[i], agents[j]     # soprannomi per leggibilità
            d = max(abs(a.pos_x - b.pos_x), abs(a.pos_y - b.pos_y))  # distanza di Chebyshev
            if d > 1:                       # se sono lontani, salta questa coppia
                continue
            if a.state == 'I' and b.state == 'S':       # a è malato, b è sano
                if np.random.rand() < cfg.beta:          # tira il dado
                    b.state = 'I'                        # b si infetta
            elif a.state == 'S' and b.state == 'I':     # b è malato, a è sano
                if np.random.rand() < cfg.beta:          # tira il dado
                    a.state = 'I'                        # a si infetta


# --- GUARIGIONE ---
# Cosa fa: ogni agente infetto, ad ogni tick, ha probabilità gamma di guarire (I → R).
# NetLogo: ask turtles with [state='I'] [ if random-float 1 < gamma [ set state 'R' ] ]
# Identica nel continuo e nel discreto: la guarigione non dipende dalla posizione nello spazio.
# Non ha return: modifica direttamente gli oggetti nella lista — le modifiche si vedono fuori.
def guarigione(agents, cfg):
    for a in agents:                        # scorre tutti gli agenti
        if a.state == 'I':                  # considera solo gli infetti
            if np.random.rand() < cfg.gamma: # tira il dado
                a.state = 'R'              # guarisce


# --- CONTEGGIO STATI ---
# Cosa fa: conta quanti agenti sono S, I, R in questo momento.
# NetLogo: count turtles with [state='S'] — usato nei monitor e nei plot.
# Come si legge: sum(1 for a in agents if a.state == 'S') significa
#   "per ogni agente, se il suo stato è S, aggiungi 1 e somma tutto".
#   Come mettere una tacca ogni volta che trovi un agente S e contare le tacche alla fine.
# Alternativa con if/elif/else — identica ma più lunga:
#   s, i, r = 0, 0, 0
#   for a in agents:
#       if a.state == 'S':   s += 1
#       elif a.state == 'I': i += 1
#       elif a.state == 'R': r += 1
# return s, i, r restituisce tre valori insieme (una tupla) — chi chiama la funzione
#   li riceve separati con: s, i, r = conta_stati(agents)  (unpacking).
def conta_stati(agents):
    s = sum(1 for a in agents if a.state == 'S')  # conta gli S: per ogni agente S aggiungi 1
    i = sum(1 for a in agents if a.state == 'I')  # conta gli I
    r = sum(1 for a in agents if a.state == 'R')  # conta gli R
    return s, i, r                                # restituisce i tre valori insieme (tupla)


# --- LOOP PRINCIPALE ---
# Cosa fa: è il motore della simulazione — esegue tutte le dinamiche per cfg.days giorni
#   e raccoglie i dati giorno per giorno.
# NetLogo: pulsante "go" → repeat days [ muovi  contagio  guarigione  aggiorna-plot ]
# history è un dizionario con tre liste vuote. Ad ogni giorno si aggiunge un numero:
#   history['S'] = [35, 34, 33, ...]  → quanti S c'erano ogni giorno
# Perché un dizionario: si potevano usare tre liste separate (history_s, history_i, history_r)
#   ma sarebbe molto più scomodo — tre variabili da passare ovunque invece di una sola.
#   Con il dizionario tutto è insieme e history['S'] è più leggibile di history[0].
# L'ordine delle chiamate conta: prima ci si muove, poi si interagisce con chi è vicino.
# return history è obbligatorio: history è creato qui dentro — senza return va perso.
def run_simulation(cfg):
    agents = crea_agenti(cfg)              # crea tutti gli agenti — si fa una volta sola
    history = {'S': [], 'I': [], 'R': []} # dizionario con tre liste vuote per raccogliere i dati
    snapshots = []                         # lista di liste di tuple: una snap per ogni giorno → snapshots[giorno][agente][campo]

    for day in range(cfg.days):            # ripete per ogni giorno della simulazione
        muovi_agenti(agents, cfg)          # 1. ogni agente si sposta
        contagio(agents, cfg)              # 2. chi è vicino si contagia
        guarigione(agents, cfg)            # 3. chi è infetto forse guarisce
        s, i, r = conta_stati(agents)      # 4. conta quanti S, I, R ci sono oggi
        history['S'].append(s)             # salva il conteggio S di oggi
        history['I'].append(i)             # salva il conteggio I di oggi
        history['R'].append(r)             # salva il conteggio R di oggi

        snap = [(a.pos_x, a.pos_y, a.state) for a in agents]  # lista di tuple: una tupla (x, y, stato) per ogni agente
        snapshots.append(snap)             # aggiunge snap a snapshots → snapshots[0][1][2] = stato dell'agente 1 al giorno 0

    return history, snapshots              # restituisce sia i conteggi che le posizioni


# --- COLORI PER STATO ---
# Dizionario che associa ogni stato SIR a un colore — usato nell'animazione.
# In MAIUSCOLO perché è una costante: non cambia mai durante la simulazione.
STATE_COLORS = {'S': 'steelblue', 'I': 'crimson', 'R': 'seagreen'}  # S=blu, I=rosso, R=verde


# --- ANIMAZIONE ---
# Cosa fa: crea una GIF animata che mostra gli agenti sulla griglia mentre si muovono e cambiano stato.
# NetLogo: la vista grafica con le tartarughe colorate che si muovono tick per tick.
# Perché FuncAnimation: è la funzione standard di matplotlib per animare grafici frame per frame.
#   Ogni frame corrisponde a un giorno — update() viene chiamata una volta per frame.
# Come si legge: apre la finestra → prepara il grafico vuoto → per ogni giorno aggiorna
#   le posizioni e i colori degli agenti → salva tutto come GIF.
# snapshots è la lista di liste costruita in run_simulation — ogni elemento è un giorno.
def crea_animazione(snapshots, cfg, filename='SIR_animazione.gif'):
    fig, ax = plt.subplots(figsize=(6, 6))                              # apre la finestra quadrata
    ax.set_xlim(-cfg.grid_size - 0.5, cfg.grid_size + 0.5)             # limiti centrati sulle celle 
    ax.set_ylim(-cfg.grid_size - 0.5, cfg.grid_size + 0.5)             # idem asse Y
    ax.set_aspect('equal')                                              # celle quadrate
    ax.set_title('Modello SIR — spazio discreto')                      # titolo del grafico

    # Le linee della griglia vanno a ±0.5 rispetto alle coordinate intere degli agenti,
    # così l'agente appare al suo centro.
    ticks_x = [x - 0.5 for x in range(-cfg.grid_size, cfg.grid_size + 2)]  # bordi delle colonne
    ticks_y = [y - 0.5 for y in range(-cfg.grid_size, cfg.grid_size + 2)]  # bordi delle righe
    ax.set_xticks(ticks_x)                                              # posiziona le linee verticali
    ax.set_yticks(ticks_y)                                              # posiziona le linee orizzontali
    ax.tick_params(labelbottom=False, labelleft=False)                  # nasconde i numeri sui tick
    ax.grid(True, color='lightgray', linewidth=0.5, zorder=0)          # disegna la griglia sotto gli agenti

    legend_patches = [Patch(color=c, label=s) for s, c in STATE_COLORS.items()]  # rettangolini colorati per la legenda
    ax.legend(handles=legend_patches, loc='upper right')               # mostra la legenda in alto a destra

    scatter = ax.scatter([], [], s=50)                                  # segnaposto vuoto per i punti degli agenti
    day_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)         # testo "Giorno N" nell'angolo in alto a sinistra

    def update(frame):                                                  # chiamata una volta per ogni frame (giorno)
        snap = snapshots[frame]                                         # prende lo snapshot del giorno corrente
        xs     = [p[0] for p in snap]                                  # estrae tutte le posizioni X
        ys     = [p[1] for p in snap]                                  # estrae tutte le posizioni Y
        colors = [STATE_COLORS[p[2]] for p in snap]                    # associa un colore a ogni stato
        scatter.set_offsets(list(zip(xs, ys)))                         # aggiorna le posizioni dei punti
        scatter.set_color(colors)                                       # aggiorna i colori dei punti
        day_text.set_text(f'Giorno {frame}')                           # aggiorna il contatore giorno
        return scatter, day_text                                        # restituisce gli oggetti aggiornati

    anim = animation.FuncAnimation(fig, update, frames=len(snapshots), interval=100, blit=True)  # crea l'animazione
    anim.save(filename, writer='pillow', fps=10)                        # salva come GIF (richiede pillow installato)
    print(f'GIF salvata come {filename}')                              # conferma a schermo
    plt.close()                                                         # chiude la finestra — la GIF è già salvata


# --- VISUALIZZAZIONE ---
# Cosa fa: plotta le curve S, I, R nel tempo con matplotlib.
# NetLogo: plot monitor → "plot count turtles with [state='S']" ecc.
# history contiene le liste con i conteggi di ogni giorno — plt.plot le disegna come curve.
def plot_risultati(history):
    giorni = range(len(history['S']))  # asse X: 0, 1, 2, ... giorni totali
    plt.figure(figsize=(9, 5))         # apre la finestra del grafico (larghezza x altezza in pollici)
    plt.plot(giorni, history['S'], label='Susceptible', color='steelblue')  # curva S
    plt.plot(giorni, history['I'], label='Infected',    color='crimson')    # curva I
    plt.plot(giorni, history['R'], label='Recovered',   color='seagreen')   # curva R
    plt.xlabel('Giorni')               # etichetta asse X
    plt.ylabel('Numero di agenti')     # etichetta asse Y
    plt.title('Modello SIR — spazio discreto')          # titolo in cima
    plt.legend()                       # mostra la legenda — senza questa le label non appaiono
    plt.tight_layout()                 # aggiusta i margini per non tagliare titolo o etichette
    plt.show()                         # apre la finestra — senza questa il grafico non appare


# --- ENTRY POINT ---
# Cosa fa: avvia tutto quando il file viene eseguito direttamente.
# cfg = config() crea l'istanza.
# NetLogo: equivalente al click su "Setup" poi "Go".
if __name__ == "__main__":
    cfg = config()                          # crea l'istanza con i parametri di default
    history, snapshots = run_simulation(cfg) # avvia la simulazione — raccoglie dati e posizioni
    plot_risultati(history)                 # disegna il grafico S/I/R nel tempo
    crea_animazione(snapshots, cfg)         # salva la GIF animata nella stessa cartella
