import sys
import networkx as nx
import matplotlib.pyplot as plt
import io
import base64
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def dijkstra(grafo, nodo_inicial):
    etiquetas = {}
    visitados = []
    pendientes = [nodo_inicial]
    nodo_actual = nodo_inicial

    etiquetas[nodo_actual] = [0, '']

    while len(pendientes) > 0:
        nodo_actual = nodo_menor_peso(etiquetas, visitados)
        visitados.append(nodo_actual)

        for adyacente, peso in grafo[nodo_actual].items():
            if adyacente not in pendientes and adyacente not in visitados:
                pendientes.append(adyacente)
            nuevo_peso = etiquetas[nodo_actual][0] + grafo[nodo_actual][adyacente]
            if adyacente not in visitados:
                if adyacente not in etiquetas:
                    etiquetas[adyacente] = [nuevo_peso, nodo_actual]
                else:
                    if etiquetas[adyacente][0] > nuevo_peso:
                        etiquetas[adyacente] = [nuevo_peso, nodo_actual]
        del pendientes[pendientes.index(nodo_actual)]
    
    return etiquetas

def nodo_menor_peso(etiquetas, visitados):
    menor = sys.maxsize
    for nodo, etiqueta in etiquetas.items():
        if etiqueta[0] < menor and nodo not in visitados:
            menor = etiqueta[0]
            nodo_menor = nodo
    return nodo_menor

def obtener_camino(etiquetas, nodo_final):
    camino = []
    nodo = nodo_final
    while nodo != '':
        camino.insert(0, nodo)
        nodo = etiquetas[nodo][1]  
    return camino

def generar_imagen(grafo, camino):
    G = nx.Graph()
    
    for nodo, adyacentes in grafo.items():
        for adyacente, peso in adyacentes.items():
            G.add_edge(nodo, adyacente, weight=peso)
    
    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color='lightblue')
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5, edge_color='gray')
    nx.draw_networkx_labels(G, pos, font_size=12, font_color='black')
    
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    
    if camino:
        camino_aristas = list(zip(camino, camino[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=camino_aristas, width=2.5, edge_color='red')
    
    plt.title("Grafo con el camino más corto en rojo")
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    
    return img_base64

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calcular', methods=['POST'])
def calcular():
    num_nodos = int(request.form['num_nodos'])
    grafo = {}
    
    for i in range(num_nodos):
        adyacentes = {}
        num_adyacentes = int(request.form[f'num_adyacentes_{i}'])
        for j in range(num_adyacentes):
            adyacente = int(request.form[f'adyacente_{i}_{j}_nodo'])
            peso = int(request.form[f'adyacente_{i}_{j}_peso'])
            adyacentes[adyacente] = peso
        grafo[i] = adyacentes
    
    nodo_inicial = int(request.form['nodo_inicial'])
    nodo_final = int(request.form['nodo_final'])

    etiquetas = dijkstra(grafo, nodo_inicial)
    camino = obtener_camino(etiquetas, nodo_final)
    
    imagen_base64 = generar_imagen(grafo, camino)
    
    return jsonify({
        'camino': ' -> '.join(map(str, camino)),
        'distancia': etiquetas[nodo_final][0],
        'imagen_base64': imagen_base64
    })

if __name__ == '__main__':
    # Obtener el puerto desde la variable de entorno, si no está presente usar el puerto 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)