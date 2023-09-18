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
    points_data = request.form.get('points')
    global selected_points

    selected_points = json.loads(points_data)
    print(selected_points)
    cache.set('selected_points', selected_points)

    return render_template('passo2.html', pontos=selected_points)


def formatar_estilo(estilo):
    estilo_formatado = ''
    for propriedade in estilo:
        propriedade_formatada = propriedade.strip('\'" ')
        valor_formatado = estilo[propriedade].strip('\'" ')
        if propriedade_formatada == 'backgroundColor':
            propriedade_formatada = 'background-color'
        estilo_formatado += f"{propriedade_formatada}: {valor_formatado}; "
    return estilo_formatado


@app.route('/passo3', methods=['POST'])
def passo3():
    arestas_data = request.form['edges']
    arestas = json.loads(arestas_data)
    selected_points = cache.get('selected_points')
    arestas_s = json.loads(arestas_data)
    cache.set('arestas_s', arestas_s)

    for aresta in arestas:
        estilo_formatado = formatar_estilo(aresta['style'])
        aresta['style'] = estilo_formatado
        print(estilo_formatado)

    return render_template('passo3.html', pontos=selected_points, arestas=arestas)


def has_cycle(graph, edge):
    return nx.has_path(graph, edge['name'][1], edge['name'][0])

def find_longest_path(graph, start):
    def dfs(node, path):
        nonlocal longest_path
        path.append(node)
        for neighbor in graph.neighbors(node):
            if neighbor not in path:
                dfs(neighbor, path)
        if len(path) > len(longest_path):
            longest_path = path.copy()

    longest_path = []
    dfs(start, [])
    return longest_path

@app.route('/passo4', methods=['POST'])
def passo4():
    selected_edges_json = request.form.get('selectedEdges')
    selected_points = cache.get('selected_points')

    if selected_edges_json:
        selected_edges = json.loads(selected_edges_json)

        # Crie um grafo ponderado não direcionado
        G = nx.Graph()
        for edge in selected_edges:
            name = edge['name']
            weight = edge['weight']
            estilo = edge['estilo']
            G.add_edge(name[0], name[1], weight=int(weight), estilo=estilo)

        # Calcule a MST usando o algoritmo de Kruskal
        mst = nx.minimum_spanning_tree(G)

        # Extraia as arestas da MST
        mst_edges = []
        for u, v, data in mst.edges(data=True):
            weight = data['weight']
            estilo = data['estilo']
            mst_edges.append({'name': (u, v), 'weight': weight, 'estilo': estilo})

        mst_edges.sort(key=lambda x: x['weight'])

        # Encontre o caminho mais longo
        start_node = list(G.nodes())[0]
        longest_path_edges = find_longest_path(G, start_node)

        # Encontre os ciclos evitados
        cycle_edges = []
        for cycle in nx.simple_cycles(G):
            if len(cycle) > 3:
                for i in range(len(cycle) - 1):
                    edge_name = (cycle[i], cycle[i + 1])
                    weight = G.get_edge_data(*edge_name)['weight']
                    estilo = G.get_edge_data(*edge_name)['estilo']
                    cycle_edges.append({'name': edge_name, 'weight': weight, 'estilo': estilo})
                edge_name = (cycle[-1], cycle[0])
                weight = G.get_edge_data(*edge_name)['weight']
                estilo = G.get_edge_data(*edge_name)['estilo']
                cycle_edges.append({'name': edge_name, 'weight': weight, 'estilo': estilo})

        return render_template('passo4.html', mst_edges=mst_edges, longest_path_edges=longest_path_edges, cycle_edges=cycle_edges, pontos=selected_points)

    else:
        return render_template('passo4_no_selection.html')

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
