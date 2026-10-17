import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.PriorityQueue;

/**
 * Algoritmo de Dijkstra (caminhos mínimos a partir de uma origem).
 *
 * Estratégia gulosa: a cada passo, entre os vértices ainda não finalizados,
 * escolhe-se o de MENOR distância estimada, fixa-se essa distância como
 * definitiva e relaxam-se as arestas que saem dele.
 *
 * Duas versões são oferecidas:
 *  - executarComHeap  : fila de prioridade (heap binário), O((V + E) log V)
 *  - executarComVetor : busca linear pelo mínimo,          O(V^2)
 *
 * Pré-condição: todos os pesos das arestas devem ser NÃO NEGATIVOS.
 */
public class Dijkstra {

    /** Valor usado para "distância infinita" (vértice ainda não alcançado). */
    public static final long INFINITO = Long.MAX_VALUE;

    // ------------------------------------------------------------------
    // Estruturas de dados
    // ------------------------------------------------------------------

    /** Aresta que sai de um vértice (o vértice de origem é implícito na lista de adjacência). */
    public static class Aresta {
        public final int destino;
        public final int peso;

        public Aresta(int destino, int peso) {
            this.destino = destino;
            this.peso = peso;
        }
    }

    /** Grafo representado por lista de adjacência. */
    public static class Grafo {
        private final int numVertices;
        private final List<List<Aresta>> adjacencia;
        private final boolean validarPesos;
        private String[] nomes;       // nomes opcionais para impressão
        private int numArestas = 0;   // arestas direcionadas armazenadas

        public Grafo(int numVertices) {
            this(numVertices, true);
        }

        /**
         * @param validarPesos se true, rejeita pesos negativos (comportamento correto
         *                     para Dijkstra). Use false apenas para demonstrar a falha
         *                     do algoritmo com pesos negativos.
         */
        public Grafo(int numVertices, boolean validarPesos) {
            if (numVertices <= 0) {
                throw new IllegalArgumentException("O grafo precisa ter ao menos 1 vértice.");
            }
            this.numVertices = numVertices;
            this.validarPesos = validarPesos;
            this.adjacencia = new ArrayList<>(numVertices);
            for (int i = 0; i < numVertices; i++) {
                adjacencia.add(new ArrayList<>());
            }
        }

        public void definirNomes(String... nomes) {
            if (nomes.length != numVertices) {
                throw new IllegalArgumentException("Quantidade de nomes diferente do número de vértices.");
            }
            this.nomes = nomes;
        }

        public String nome(int vertice) {
            return (nomes != null) ? nomes[vertice] : String.valueOf(vertice);
        }

        public void adicionarArestaDirecionada(int origem, int destino, int peso) {
            validarVertice(origem);
            validarVertice(destino);
            if (validarPesos && peso < 0) {
                throw new IllegalArgumentException(
                        "Dijkstra não aceita pesos negativos (aresta " + origem + " -> " + destino
                                + ", peso " + peso + ").");
            }
            adjacencia.get(origem).add(new Aresta(destino, peso));
            numArestas++;
        }

        public void adicionarArestaNaoDirecionada(int u, int v, int peso) {
            adicionarArestaDirecionada(u, v, peso);
            adicionarArestaDirecionada(v, u, peso);
        }

        public List<Aresta> vizinhos(int vertice) {
            return adjacencia.get(vertice);
        }

        public int getNumVertices() {
            return numVertices;
        }

        /** Número de arestas direcionadas armazenadas (uma aresta não direcionada conta 2). */
        public int getNumArestas() {
            return numArestas;
        }

        private void validarVertice(int v) {
            if (v < 0 || v >= numVertices) {
                throw new IllegalArgumentException("Vértice inválido: " + v);
            }
        }
    }

    /** Resultado da execução: distâncias mínimas e predecessores (árvore de caminhos mínimos). */
    public static class Resultado {
        public final int origem;
        public final long[] distancia;   // INFINITO se inalcançável
        public final int[] predecessor;  // -1 para a origem e para inalcançáveis

        public Resultado(int origem, long[] distancia, int[] predecessor) {
            this.origem = origem;
            this.distancia = distancia;
            this.predecessor = predecessor;
        }

        public boolean alcancavel(int vertice) {
            return distancia[vertice] != INFINITO;
        }

        /** Reconstrói o caminho origem -> destino. Lista vazia se o destino for inalcançável. */
        public List<Integer> caminhoAte(int destino) {
            List<Integer> caminho = new ArrayList<>();
            if (!alcancavel(destino)) {
                return caminho;
            }
            for (int v = destino; v != -1; v = predecessor[v]) {
                caminho.add(v);
            }
            Collections.reverse(caminho);
            return caminho;
        }
    }

    /** Entrada da fila de prioridade: vértice + distância no momento da inserção. */
    private static class NoFila implements Comparable<NoFila> {
        final int vertice;
        final long distancia;

        NoFila(int vertice, long distancia) {
            this.vertice = vertice;
            this.distancia = distancia;
        }

        @Override
        public int compareTo(NoFila outro) {
            return Long.compare(this.distancia, outro.distancia);
        }
    }

    // ------------------------------------------------------------------
    // Versão com fila de prioridade (heap) - O((V + E) log V)
    // ------------------------------------------------------------------

    /**
     * @param detalhar se true, imprime cada decisão do algoritmo (útil para a instância pequena)
     */
    public static Resultado executarComHeap(Grafo grafo, int origem, boolean detalhar) {
        int n = grafo.getNumVertices();
        long[] distancia = new long[n];
        int[] predecessor = new int[n];
        boolean[] finalizado = new boolean[n];
        Arrays.fill(distancia, INFINITO);
        Arrays.fill(predecessor, -1);

        PriorityQueue<NoFila> fila = new PriorityQueue<>();
        distancia[origem] = 0;
        fila.add(new NoFila(origem, 0));

        while (!fila.isEmpty()) {
            NoFila atual = fila.poll();
            int u = atual.vertice;

            // Entrada obsoleta: o vértice já foi finalizado com uma distância menor.
            if (finalizado[u]) {
                continue;
            }

            // ESCOLHA GULOSA: o menor da fila tem distância definitiva.
            finalizado[u] = true;
            if (detalhar) {
                System.out.println("  Escolhe " + grafo.nome(u) + " (dist = " + distancia[u] + ") -> finalizado");
            }

            for (Aresta aresta : grafo.vizinhos(u)) {
                int v = aresta.destino;
                if (finalizado[v]) {
                    continue; // decisões anteriores nunca são reconsideradas
                }
                long nova = distancia[u] + aresta.peso;
                if (nova < distancia[v]) {
                    if (detalhar) {
                        System.out.println("    relaxa " + grafo.nome(u) + " -> " + grafo.nome(v)
                                + ": " + distancia[u] + " + " + aresta.peso + " = " + nova
                                + " < " + formatar(distancia[v]) + "  => atualiza dist[" + grafo.nome(v) + "]");
                    }
                    distancia[v] = nova;
                    predecessor[v] = u;
                    fila.add(new NoFila(v, nova));
                } else if (detalhar) {
                    System.out.println("    relaxa " + grafo.nome(u) + " -> " + grafo.nome(v)
                            + ": " + distancia[u] + " + " + aresta.peso + " = " + nova
                            + " >= " + formatar(distancia[v]) + "  => mantém");
                }
            }
        }
        return new Resultado(origem, distancia, predecessor);
    }

    // ------------------------------------------------------------------
    // Versão com vetor (busca linear do mínimo) - O(V^2)
    // ------------------------------------------------------------------

    public static Resultado executarComVetor(Grafo grafo, int origem, boolean detalhar) {
        int n = grafo.getNumVertices();
        long[] distancia = new long[n];
        int[] predecessor = new int[n];
        boolean[] finalizado = new boolean[n];
        Arrays.fill(distancia, INFINITO);
        Arrays.fill(predecessor, -1);
        distancia[origem] = 0;

        for (int iteracao = 0; iteracao < n; iteracao++) {
            // ESCOLHA GULOSA: varre o vetor procurando o não finalizado de menor distância.
            int u = -1;
            long menor = INFINITO;
            for (int v = 0; v < n; v++) {
                if (!finalizado[v] && distancia[v] < menor) {
                    menor = distancia[v];
                    u = v;
                }
            }
            if (u == -1) {
                break; // os restantes são inalcançáveis
            }

            finalizado[u] = true;
            if (detalhar) {
                System.out.println("  Escolhe " + grafo.nome(u) + " (dist = " + distancia[u] + ") -> finalizado");
            }

            for (Aresta aresta : grafo.vizinhos(u)) {
                int v = aresta.destino;
                if (finalizado[v]) {
                    continue;
                }
                long nova = distancia[u] + aresta.peso;
                if (nova < distancia[v]) {
                    distancia[v] = nova;
                    predecessor[v] = u;
                }
            }
        }
        return new Resultado(origem, distancia, predecessor);
    }

    /** Formata distância para impressão ("INF" quando infinita). */
    public static String formatar(long distancia) {
        return (distancia == INFINITO) ? "INF" : String.valueOf(distancia);
    }
}