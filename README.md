# ABMpy — Da NetLogo a Python

**Una guida open source per chi viene da NetLogo e vuole imparare a costruire modelli ad agenti in Python.**

> Questo progetto è nato da un bisogno personale: capire come tradurre quello che già sapevo fare in NetLogo nel linguaggio con cui lavora la ricerca computazionale moderna. Se anche tu ti sei trovata/o con un modello NetLogo in mano e non sapevi da dove cominciare in Python, sei nel posto giusto.

---

## Di cosa si tratta

Una raccolta di **guide e dizionari** che affiancano codice NetLogo e codice Python equivalente, spiegando non solo *come* si scrive ma *perché* — il ragionamento dietro ogni scelta.

Il progetto parte dal **modello SIR** (un modello epidemiologico classico, semplice ma completo) come filo conduttore, ma l'obiettivo è diventare una risorsa generale per chiunque voglia fare il salto da NetLogo a Python.

### Cosa c'è già

| Pagina | Contenuto |
|--------|-----------|
| [Guida — Modello SIR](index.html) | Traduzione passo-passo di un modello epidemiologico da NetLogo a Python: agente, movimento, contagio, guarigione, ciclo principale, visualizzazione, e una ricetta generale per costruire qualsiasi ABM da zero |
| [Dizionario — Modello SIR](dizionario.html) | Glossario dei termini e costrutti usati nel modello, con equivalenti NetLogo e Python a confronto |

---

## Come nasce questo progetto

Ho iniziato a usare NetLogo per costruire modelli ad agenti, e ad un certo punto mi sono resa conto che la ricerca e i progetti più seri usano Python. Il problema è che il salto non è ovvio: NetLogo ha una sintassi propria, un'interfaccia grafica, un modo di pensare agli agenti che non si mappa direttamente su nessuna libreria Python esistente.

Ho cercato risorse in italiano che spiegassero questa transizione in modo diretto — non trovandole, ho cominciato a costruirle io stessa. Questo è il risultato.

**Non sono una sviluppatrice esperta.** Ho imparato facendo, e questa guida riflette il percorso di qualcuno che arriva da NetLogo, non di qualcuno che conosce già Python a fondo. Questo è sia il suo limite che il suo punto di forza: è scritta dalla prospettiva di chi impara, per chi impara.

---

## Vuoi contribuire?

Questo è un progetto collaborativo. Se sai più di me — e probabilmente è così — il tuo contributo è prezioso.

### Cosa sarebbe utile

- **Correzioni**: se hai trovato un errore concettuale, un'imprecisione, o un modo migliore di spiegare qualcosa, apri una Issue o una Pull Request.
- **Nuovi modelli**: la struttura della guida SIR è replicabile su altri modelli classici (Schelling, Boids, SIS, SEIR...). Se vuoi contribuire una guida per un nuovo modello, scrivi.
- **Miglioramenti al codice Python**: il codice nei blocchi è scritto per essere leggibile, non necessariamente ottimale. Se hai suggerimenti su performance, idiomi Python più corretti, o usi migliori delle librerie, sono interessata ad ascoltarli.
- **Traduzioni**: le guide sono in italiano perché l'italiano è la mia lingua e perché mancano risorse ABM in italiano. Se vuoi contribuire una versione in inglese, sei il benvenuto.
- **Feedback didattico**: se hai usato queste pagine per insegnare o imparare e hai suggerimenti su cosa non era chiaro, è esattamente il tipo di feedback che mi serve.

### Come contribuire

1. Apri una **Issue** per segnalare errori o proporre aggiunte — anche solo un commento è utile.
2. Fai **fork** del repo e apri una **Pull Request** con le tue modifiche.
3. Scrivi nei **Discussions** se vuoi proporre qualcosa di più grande prima di metterti a scrivere.

Non serve essere esperti di GitHub. Anche una Issue scritta in italiano con "ho trovato questo errore" va benissimo.

---

## Come vedere le pagine

Il progetto è pubblicato su **GitHub Pages** all'indirizzo:

```
https://CarolinaCrespi.github.io/abm-netlogo-python/
```

---

## Struttura del repository

```
abm-netlogo-python/
├── README.md
├── index.html          ← guida passo-passo: da NetLogo a Python
├── dizionario.html     ← glossario termini con confronto NetLogo / Python
└── og-image.png        ← anteprima social
```

---

## Licenza

[MIT](LICENSE) — liberamente riutilizzabile, con attribuzione.

---

*Fatto con curiosità e molta pazienza. Se ti è stato utile, lascia una ⭐ — fa piacere sapere che non è solo per me.*
