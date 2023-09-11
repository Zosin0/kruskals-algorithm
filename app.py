from flask import Flask, render_template, request, redirect, url_for, jsonify 
import networkx as nx
import json

app = Flask(__name__)


@app.route('//')
def home():
    return render_template('index.html')

@app.route('/jogo')
def index():
    return render_template('jogo.html')

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
