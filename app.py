from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_caching import Cache
from networkx.algorithms import find_cycle
import networkx as nx
import json
import math
import gzip

app = Flask(__name__)
app.config['CACHE_TYPE'] = 'simple'
cache = Cache(app)


#  INICIO -> Entendendo Conceitos e Passos #
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/1')
def p1():
    return render_template('1.html')


@app.route('/2')
def p2():
    return render_template('2.html')


@app.route('/3')
def p3():
    return render_template('3.html')


@app.route('/4')
def p4():
    return render_template('4.html')


@app.route('/5')
def p5():
    return render_template('5.html')


@app.route('/jogar')
def jogo1():
    return render_template('jogo1.html')


@app.route('/pagina_do_tesouro')
def tesouro():
    return render_template('pagina_do_tesouro.html')


#  FIM -> Entendendo Conceitos e Passos #

#  INICIO -> Entendendo o Algoritmo #
@app.route('/jogo', methods=['GET', 'POST'])
def index():
    return render_template('jogo.html')


@app.route('/resultado', methods=['POST'])
def resultado():
    selected_edges_json = request.form.get('selectedEdges')
    arestas_s = json.loads(selected_edges_json)
    cache.set('arestas_s', arestas_s)

    if selected_edges_json:
        selected_edges = json.loads(selected_edges_json)
        G = nx.DiGraph()

        for edge in selected_edges:
            name = edge['name']
            weight = edge['weight']
            G.add_edge(name[0], name[1], weight=int(weight))
            print()
            print(G)

        mst = nx.minimum_spanning_tree(G.to_undirected())
        mst_edges = []

        for edge in mst.edges(data=True):
            name = f"{edge[0]}{edge[1]}"
            weight = edge[2]['weight']
            mst_edges.append({'name': name, 'weight': weight})
            print(mst_edges)

        mst_edges.sort(key=lambda x: x['weight'])

        if len(mst_edges) != 4:
            return '<h1>O numero de arestas selecionado não é suficiente, selecione todas!</h1>'
        return render_template('resultado.html', mst_edges=mst_edges)

    else:
        return "Nenhuma aresta selecionada."


#  FIM -> Entendendo o Algoritmo #

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

def calcular_angulo(ponto1, ponto2):
    return math.degrees(math.atan2(ponto2['y'] - ponto1['y'], ponto2['x'] - ponto1['x']))


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
@app.route('/passo4', methods=['POST', 'GET'])
def passo4():
    selected_edges_json = request.form.get('selectedEdges')
    pontos = cache.get('selected_points')

    if selected_edges_json:
        selected_edges = json.loads(selected_edges_json)

        # Verifique se as arestas estão em ordem crescente de peso
        sorted_edges = sorted(selected_edges, key=lambda edge: float(edge['weight']))
        if selected_edges != sorted_edges:
            return '<h1>Por favor, insira as arestas em ordem crescente de peso.</h1>'

        # Renomeie as arestas para tornar os nomes únicos
        for i, edge in enumerate(selected_edges):
            edge['name'] = f'aresta_{i + 1}'

        # Inicialize o grafo e listas de MST e ciclos
        G = nx.Graph()
        mst_edges = []
        cycle_edges = []

        for edge in selected_edges:
            name = edge['name']
            weight = float(edge['weight'])
            estilo = edge['estilo']
            G.add_edge(name[0], name[1], weight=weight, estilo=estilo)

        # Inicialize um conjunto para rastrear os vértices visitados
        visited = set()

        # Função para percorrer o grafo em busca de ciclos
        def dfs(v, parent):
            visited.add(v)
            for neighbor in G.neighbors(v):
                if neighbor not in visited:
                    if dfs(neighbor, v):
                        return True
                elif neighbor != parent:
                    return True
            return False

        # Verifique se a adição da aresta gera um ciclo
        for edge in selected_edges:
            name = edge['name']
            if not dfs(name[0], None):
                # Se não gerar ciclo, adicione à lista de possíveis arestas da MST
                mst_edges.append(edge)

        # Ordenar as arestas da MST por peso
        mst_edges = sorted(mst_edges, key=lambda edge: float(edge['weight']))

        # Verifica se o grafo é desconexo (mais de uma árvore)
        num_trees = len(list(nx.connected_components(G)))
        if num_trees > 1:
            tree_type = 'floresta'  # Mais de uma árvore
        else:
            tree_type = 'árvore única'

        # Calcule o caminho mais longo possível (você pode implementar isso posteriormente)

        # Inicialize o caminho mais longo como vazio por enquanto
        longest_path = []

        print(f"MST: {mst_edges}")
        print(f"Ciclos: {cycle_edges}")
        print(f"Tipo de Arvore: {tree_type}")
        print(f"Vertices: {pontos}")
        print(f"Caminho Mais Longo: {longest_path}")

        # Renderize a página passo4.html com as informações
        return render_template(
            'passo4.html',
            mst_edges=mst_edges,
            cycle_edges=cycle_edges,
            tree_type=tree_type,
            longest_path=longest_path,
            pontos=pontos
        )

    else:
        return '<h1></h1>'



#  FIM -> Entendendo o Algoritmo #





if __name__ == '__main__':
    app.run(debug=True)
