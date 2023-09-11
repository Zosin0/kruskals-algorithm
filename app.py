from flask import Flask, render_template, request, redirect, url_for, jsonify 
import networkx as nx
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/resultado', methods=['POST'])
def resultado():
    selected_edges_json = request.form.get('selectedEdges')

    if selected_edges_json:
        selected_edges = json.loads(selected_edges_json)
        G = nx.DiGraph()
        for edge in selected_edges:
            name = edge['name']
            weight = edge['weight']
            G.add_edge(name[0], name[1], weight=int(weight))

        # Use o algoritmo de Kruskal para calcular a MST
        mst = nx.minimum_spanning_tree(G.to_undirected())

        # Crie uma lista de arestas da MST
        mst_edges = []
        for edge in mst.edges(data=True):
            name = f"{edge[0]}{edge[1]}"
            weight = edge[2]['weight']
            mst_edges.append({'name': name, 'weight': weight})

        # Ordene as arestas por peso
        mst_edges.sort(key=lambda x: x['weight'])

        # Verificação de ciclo pelo nome
        def has_cycle(graph, edge):
            return nx.has_path(graph, edge['name'][1], edge['name'][0])

        # Remova arestas que formam ciclos
        mst_edges = [edge for edge in mst_edges if not has_cycle(mst, edge)]

        print(mst_edges)
        return render_template('resultado.html', mst_edges=mst_edges)
        
    else:
        return "Nenhuma aresta selecionada."
    
if __name__ == '__main__':
    app.run(debug=True)
