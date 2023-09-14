from flask import Flask, render_template, request, redirect, url_for, jsonify 
import networkx as nx
import json

app = Flask(__name__)


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

    return render_template('passo2.html', pontos=selected_points)

@app.route('/passo3', methods=['POST'])
def passo3():
    distancias = request.form.getlist('distancias[]')

    # Valide as distâncias conforme necessário antes de prosseguir.

    return render_template('passo3.html', distancias=distancias)

@app.route('/passo4')
def passo4():
    arestas_data = request.form.get('arestas')
    arestas = json.loads(arestas_data)
    print(arestas)

    return render_template('passo4.html', arestas=arestas)


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
