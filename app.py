from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_caching import Cache
import networkx as nx
import json
import math

app = Flask(__name__)
app.config['CACHE_TYPE'] = 'simple'  
cache = Cache(app)

def calcular_angulo(ponto1, ponto2):
    return math.degrees(math.atan2(ponto2['y'] - ponto1['y'], ponto2['x'] - ponto1['x']))


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/jogo')
def index():
    return render_template('jogo.html')

@app.route('/passo1')
def passo1():
    return render_template('passo1.html')

@app.route('/passo2', methods=['POST'])
def passo2():
    global selected_points
    points_data = request.form.get('points')

    selected_points = json.loads(points_data)
    cache.set('selected_points', selected_points)

    return render_template('passo2.html', pontos=selected_points)

@app.route('/passo3', methods=['POST'])
def passo3():
    arestas_data = request.form['edges']
    arestas = json.loads(arestas_data)
    selected_points = cache.get('selected_points')

    def calcular_distancia(ponto1, ponto2):
        diff_x = ponto2['x'] - ponto1['x']
        diff_y = ponto2['y'] - ponto1['y']
        
        distancia = math.sqrt(diff_x ** 2 + diff_y ** 2)
        
        return distancia


    for aresta in arestas:
        aresta['angulo'] = calcular_angulo(aresta['ponto1'], aresta['ponto2'])
        aresta['largura'] = calcular_distancia(aresta['ponto1'], aresta['ponto2'])  

    if not selected_points:
        return "Nenhum ponto selecionado."

    return render_template('passo3.html', pontos=selected_points, arestas=arestas)  

@app.route('/passo4', methods=['POST'])
def passo4():
    selected_edges_json = request.form.get('selectedEdges')

    if selected_edges_json:
        selected_edges = json.loads(selected_edges_json)
        G = nx.DiGraph()
        for edge in selected_edges:
            print(edge)
            name = edge['name']
            weight = edge['weight']
            G.add_edge(name[0], name[1], weight=int(weight))

        mst = nx.minimum_spanning_tree(G.to_undirected())

        mst_edges = []
        for edge in mst.edges(data=True):
            name = f"{edge[0]}{edge[1]}"
            weight = edge[2]['weight']
            mst_edges.append({'name': name, 'weight': weight})
            print(mst_edges)

        mst_edges.sort(key=lambda x: x['weight'])

        def has_cycle(graph, edge):
            return nx.has_path(graph, edge['name'][1], edge['name'][0])

        if len(mst_edges) != 4:
            return '<h1>O mestre Kruskal não conseguiu encontrar o tesouro, tente novamente</h1>'
        
        print(mst_edges)

        return render_template('passo4.html', mst_edges=mst_edges)
    


@app.route('/resultado', methods=['POST'])
def resultado():
    selected_edges_json = request.form.get('selectedEdges')

    if selected_edges_json:
        selected_edges = json.loads(selected_edges_json)
        G = nx.DiGraph()
        for edge in selected_edges:
            print(edge)
            name = edge['name']
            weight = edge['weight']
            G.add_edge(name[0], name[1], weight=int(weight))

        mst = nx.minimum_spanning_tree(G.to_undirected())

        mst_edges = []
        for edge in mst.edges(data=True):
            name = f"{edge[0]}{edge[1]}"
            weight = edge[2]['weight']
            mst_edges.append({'name': name, 'weight': weight})
            print(mst_edges)

        mst_edges.sort(key=lambda x: x['weight'])

        def has_cycle(graph, edge):
            return nx.has_path(graph, edge['name'][1], edge['name'][0])

        if len(mst_edges) != 4:
            return '<h1>O mestre Kruskal não conseguiu encontrar o tesouro, tente novamente</h1>'
        return render_template('resultado.html', mst_edges=mst_edges)
        
    else:
        return "Nenhuma aresta selecionada."
    
if __name__ == '__main__':
    app.run(debug=True)
