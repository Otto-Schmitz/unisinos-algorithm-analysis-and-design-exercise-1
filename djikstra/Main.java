import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Random;

/**
 * Executa o algoritmo de Dijkstra e roda a bateria de testes da atividade:
 *  Teste 1 - instância pequena  (passo a passo, resultado conferido à mão)
 *  Teste 2 - instância média    (conferida contra Bellman-Ford, um algoritmo independente)
 *  Teste 3 - instância grande   (desempenho + verificação de corretude)
 *  Teste 4 - casos de borda     (inalcançável, vértice único, peso negativo)
 *
 * Como executar:
 *   javac Dijkstra.java Main.java
 *   java Main
 */
public class Main {

    private static int totalVerificacoes = 0;
    private static int falhas = 0;

    public static void main(String[] args) {
        testePequeno();
        testeMedio();
        testeGrande();
        testeCasosDeBorda();

        System.out.println();
        System.out.println("==================================================");
        System.out.println("Resumo: " + (totalVerificacoes - falhas) + "/" + totalVerificacoes + " verificações passaram.");
        if (falhas > 0) {
            System.out.println("ATENÇÃO: " + falhas + " verificação(ões) falharam.");
            System.exit(1);
        }
    }

    // ------------------------------------------------------------------
    // TESTE 1 - Pequena instância
    // ------------------------------------------------------------------
    private static void testePequeno() {
        cabecalho("TESTE 1 - Pequena instância (6 vértices, 9 arestas)");

        Dijkstra.Grafo g = new Dijkstra.Grafo(6);
        g.definirNomes("A", "B", "C", "D", "E", "F");
        int A = 0, B = 1, C = 2, D = 3, E = 4, F = 5;
        g.adicionarArestaNaoDirecionada(A, B, 7);
        g.adicionarArestaNaoDirecionada(A, C, 9);
        g.adicionarArestaNaoDirecionada(A, F, 14);
        g.adicionarArestaNaoDirecionada(B, C, 10);
        g.adicionarArestaNaoDirecionada(B, D, 15);
        g.adicionarArestaNaoDirecionada(C, D, 11);
        g.adicionarArestaNaoDirecionada(C, F, 2);
        g.adicionarArestaNaoDirecionada(D, E, 6);
        g.adicionarArestaNaoDirecionada(E, F, 9);

        System.out.println("Entrada (grafo não direcionado), origem = A:");
        System.out.println("  A-B:7  A-C:9  A-F:14  B-C:10  B-D:15  C-D:11  C-F:2  D-E:6  E-F:9");
        System.out.println();
        System.out.println("Decisões do algoritmo (versão com heap):");
        Dijkstra.Resultado r = Dijkstra.executarComHeap(g, A, true);

        System.out.println();
        System.out.println("Solução obtida:");
        imprimirResultado(g, r);

        System.out.println();
        System.out.println("Verificações:");
        long[] esperado = {0, 7, 9, 20, 20, 11}; // calculado à mão
        verificar("distâncias iguais às calculadas à mão", Arrays.equals(esperado, r.distancia));
        verificar("caminho até E é A -> C -> F -> E", r.caminhoAte(E).equals(Arrays.asList(A, C, F, E)));
        verificar("caminho até D é A -> C -> D", r.caminhoAte(D).equals(Arrays.asList(A, C, D)));

        Dijkstra.Resultado rv = Dijkstra.executarComVetor(g, A, false);
        verificar("versão com vetor produz as mesmas distâncias", Arrays.equals(r.distancia, rv.distancia));
    }

    // ------------------------------------------------------------------
    // TESTE 2 - Média instância
    // ------------------------------------------------------------------
    private static void testeMedio() {
        cabecalho("TESTE 2 - Média instância (500 vértices, 2.500 arestas, pesos 1..100)");

        Dijkstra.Grafo g = gerarGrafoAleatorio(500, 2500, 100, 42L);
        System.out.println("Entrada: grafo aleatório conexo, semente 42, origem = 0");

        long t0 = System.nanoTime();
        Dijkstra.Resultado rHeap = Dijkstra.executarComHeap(g, 0, false);
        double msHeap = (System.nanoTime() - t0) / 1e6;

        t0 = System.nanoTime();
        Dijkstra.Resultado rVetor = Dijkstra.executarComVetor(g, 0, false);
        double msVetor = (System.nanoTime() - t0) / 1e6;

        long[] referencia = bellmanFord(g, 0);

        System.out.printf("Tempo (heap): %.3f ms | Tempo (vetor): %.3f ms%n", msHeap, msVetor);
        System.out.println("Alguns resultados (origem 0):");
        for (int destino : new int[]{1, 100, 250, 499}) {
            System.out.println("  dist[" + destino + "] = " + Dijkstra.formatar(rHeap.distancia[destino])
                    + " | caminho com " + rHeap.caminhoAte(destino).size() + " vértices");
        }

        System.out.println();
        System.out.println("Verificações:");
        verificar("heap == Bellman-Ford (algoritmo independente)", Arrays.equals(rHeap.distancia, referencia));
        verificar("vetor == Bellman-Ford", Arrays.equals(rVetor.distancia, referencia));
        verificar("certificado de otimalidade (heap)", certificado(g, rHeap));
        verificar("todos os vértices alcançáveis (grafo conexo)", todosAlcancaveis(rHeap));
    }

    // ------------------------------------------------------------------
    // TESTE 3 - Grande instância
    // ------------------------------------------------------------------
    private static void testeGrande() {
        cabecalho("TESTE 3 - Grande instância");

        // 3a) Grafo grande: apenas versão com heap (a versão O(V^2) seria inviável)
        int n = 200_000;
        int m = 1_000_000;
        System.out.println("3a) " + n + " vértices, " + m + " arestas não direcionadas, pesos 1..1000, semente 7");
        Dijkstra.Grafo g = gerarGrafoAleatorio(n, m, 1000, 7L);

        long t0 = System.nanoTime();
        Dijkstra.Resultado r = Dijkstra.executarComHeap(g, 0, false);
        double ms = (System.nanoTime() - t0) / 1e6;

        long maior = 0;
        for (long d : r.distancia) {
            if (d != Dijkstra.INFINITO && d > maior) {
                maior = d;
            }
        }
        System.out.printf("Tempo (heap): %.1f ms | maior distância encontrada: %d%n", ms, maior);
        verificar("certificado de otimalidade em todas as arestas", certificado(g, r));
        verificar("todos os vértices alcançáveis", todosAlcancaveis(r));

        // 3b) Comparação de escalabilidade heap x vetor (melhor de 3 execuções)
        System.out.println();
        System.out.println("3b) Escalabilidade heap x vetor (E = 5V, melhor de 3 execuções):");
        System.out.printf("  %8s | %10s | %12s | %12s | %s%n", "V", "E", "heap (ms)", "vetor (ms)", "iguais?");
        int[] tamanhos = {1_000, 2_000, 5_000, 10_000, 20_000};
        for (int v : tamanhos) {
            Dijkstra.Grafo gv = gerarGrafoAleatorio(v, 5 * v, 1000, 100L + v);
            double melhorHeap = Double.MAX_VALUE;
            double melhorVetor = Double.MAX_VALUE;
            Dijkstra.Resultado rh = null;
            Dijkstra.Resultado rv = null;
            for (int i = 0; i < 3; i++) {
                long a = System.nanoTime();
                rh = Dijkstra.executarComHeap(gv, 0, false);
                melhorHeap = Math.min(melhorHeap, (System.nanoTime() - a) / 1e6);
                a = System.nanoTime();
                rv = Dijkstra.executarComVetor(gv, 0, false);
                melhorVetor = Math.min(melhorVetor, (System.nanoTime() - a) / 1e6);
            }
            boolean iguais = Arrays.equals(rh.distancia, rv.distancia);
            System.out.printf("  %8d | %10d | %12.3f | %12.3f | %s%n", v, 5 * v, melhorHeap, melhorVetor, iguais ? "sim" : "NÃO");
            verificar("heap == vetor para V = " + v, iguais);
        }
    }

    // ------------------------------------------------------------------
    // TESTE 4 - Casos de borda
    // ------------------------------------------------------------------
    private static void testeCasosDeBorda() {
        cabecalho("TESTE 4 - Casos de borda");

        // Vértice inalcançável
        Dijkstra.Grafo g1 = new Dijkstra.Grafo(4);
        g1.adicionarArestaNaoDirecionada(0, 1, 3);
        g1.adicionarArestaNaoDirecionada(2, 3, 1);
        Dijkstra.Resultado r1 = Dijkstra.executarComHeap(g1, 0, false);
        System.out.println("Grafo com duas componentes (0-1 e 2-3), origem 0:");
        verificar("vértice 2 é inalcançável (dist = INF)", r1.distancia[2] == Dijkstra.INFINITO);
        verificar("caminho até vértice inalcançável é vazio", r1.caminhoAte(2).isEmpty());
        verificar("dist[1] = 3", r1.distancia[1] == 3);

        // Grafo com um único vértice
        Dijkstra.Grafo g2 = new Dijkstra.Grafo(1);
        Dijkstra.Resultado r2 = Dijkstra.executarComHeap(g2, 0, false);
        System.out.println("Grafo com um único vértice:");
        verificar("dist[origem] = 0", r2.distancia[0] == 0);

        // Peso negativo é rejeitado
        System.out.println("Aresta com peso negativo:");
        boolean lancou = false;
        try {
            new Dijkstra.Grafo(2).adicionarArestaDirecionada(0, 1, -5);
        } catch (IllegalArgumentException e) {
            lancou = true;
            System.out.println("  mensagem: " + e.getMessage());
        }
        verificar("peso negativo gera IllegalArgumentException", lancou);

        // Contraexemplo: com pesos negativos a escolha gulosa deixa de ser ótima
        System.out.println("Contraexemplo (validação desligada): 0->1 peso 2, 0->2 peso 3, 2->1 peso -2");
        Dijkstra.Grafo g3 = new Dijkstra.Grafo(3, false);
        g3.adicionarArestaDirecionada(0, 1, 2);
        g3.adicionarArestaDirecionada(0, 2, 3);
        g3.adicionarArestaDirecionada(2, 1, -2);
        Dijkstra.Resultado r3 = Dijkstra.executarComHeap(g3, 0, false);
        long[] correto = bellmanFord(g3, 0);
        System.out.println("  Dijkstra: dist[1] = " + r3.distancia[1] + " | Bellman-Ford (correto): dist[1] = " + correto[1]);
        verificar("Dijkstra erra com peso negativo (dist[1] = 2, mas o ótimo é 1)",
                r3.distancia[1] == 2 && correto[1] == 1);
    }

    // ------------------------------------------------------------------
    // Utilitários de geração e verificação
    // ------------------------------------------------------------------

    /**
     * Gera um grafo não direcionado conexo: primeiro uma árvore aleatória (garante conexão)
     * e depois arestas aleatórias até totalizar 'numArestas' arestas não direcionadas.
     */
    private static Dijkstra.Grafo gerarGrafoAleatorio(int numVertices, int numArestas, int pesoMaximo, long semente) {
        Random rnd = new Random(semente);
        Dijkstra.Grafo g = new Dijkstra.Grafo(numVertices);
        for (int i = 1; i < numVertices; i++) {
            int pai = rnd.nextInt(i);
            g.adicionarArestaNaoDirecionada(pai, i, 1 + rnd.nextInt(pesoMaximo));
        }
        int restantes = numArestas - (numVertices - 1);
        for (int i = 0; i < restantes; i++) {
            int u = rnd.nextInt(numVertices);
            int v = rnd.nextInt(numVertices);
            if (u == v) {
                v = (v + 1) % numVertices;
            }
            g.adicionarArestaNaoDirecionada(u, v, 1 + rnd.nextInt(pesoMaximo));
        }
        return g;
    }

    /** Bellman-Ford: algoritmo independente, usado apenas como referência para conferir resultados. */
    private static long[] bellmanFord(Dijkstra.Grafo g, int origem) {
        int n = g.getNumVertices();
        long[] dist = new long[n];
        Arrays.fill(dist, Dijkstra.INFINITO);
        dist[origem] = 0;
        for (int i = 0; i < n - 1; i++) {
            boolean mudou = false;
            for (int u = 0; u < n; u++) {
                if (dist[u] == Dijkstra.INFINITO) {
                    continue;
                }
                for (Dijkstra.Aresta a : g.vizinhos(u)) {
                    if (dist[u] + a.peso < dist[a.destino]) {
                        dist[a.destino] = dist[u] + a.peso;
                        mudou = true;
                    }
                }
            }
            if (!mudou) {
                break;
            }
        }
        return dist;
    }

    /**
     * Certificado de otimalidade (confere o resultado em O(V + E) sem recalcular):
     *  1) dist[origem] = 0;
     *  2) nenhuma aresta pode ser relaxada: dist[v] <= dist[u] + peso para toda aresta u -> v;
     *  3) cada distância é realizada por seu predecessor: dist[v] = dist[pred[v]] + peso(pred[v], v).
     * Se 1, 2 e 3 valem, as distâncias são mínimas.
     */
    private static boolean certificado(Dijkstra.Grafo g, Dijkstra.Resultado r) {
        if (r.distancia[r.origem] != 0) {
            return false;
        }
        for (int u = 0; u < g.getNumVertices(); u++) {
            if (r.distancia[u] == Dijkstra.INFINITO) {
                continue;
            }
            for (Dijkstra.Aresta a : g.vizinhos(u)) {
                if (r.distancia[a.destino] > r.distancia[u] + a.peso) {
                    return false;
                }
            }
        }
        for (int v = 0; v < g.getNumVertices(); v++) {
            if (v == r.origem || r.distancia[v] == Dijkstra.INFINITO) {
                continue;
            }
            int p = r.predecessor[v];
            if (p < 0) {
                return false;
            }
            long menorPeso = Long.MAX_VALUE;
            for (Dijkstra.Aresta a : g.vizinhos(p)) {
                if (a.destino == v && a.peso < menorPeso) {
                    menorPeso = a.peso;
                }
            }
            if (menorPeso == Long.MAX_VALUE || r.distancia[v] != r.distancia[p] + menorPeso) {
                return false;
            }
        }
        return true;
    }

    private static boolean todosAlcancaveis(Dijkstra.Resultado r) {
        for (long d : r.distancia) {
            if (d == Dijkstra.INFINITO) {
                return false;
            }
        }
        return true;
    }

    // ------------------------------------------------------------------
    // Utilitários de impressão
    // ------------------------------------------------------------------

    private static void imprimirResultado(Dijkstra.Grafo g, Dijkstra.Resultado r) {
        System.out.println("  Origem: " + g.nome(r.origem));
        for (int v = 0; v < g.getNumVertices(); v++) {
            List<String> nomes = new ArrayList<>();
            for (int vertice : r.caminhoAte(v)) {
                nomes.add(g.nome(vertice));
            }
            String caminho = nomes.isEmpty() ? "(sem caminho)" : String.join(" -> ", nomes);
            System.out.println("  " + g.nome(v) + ": distância = " + Dijkstra.formatar(r.distancia[v])
                    + " | caminho: " + caminho);
        }
    }

    private static void cabecalho(String titulo) {
        System.out.println();
        System.out.println("==================================================");
        System.out.println(titulo);
        System.out.println("==================================================");
    }

    private static void verificar(String descricao, boolean condicao) {
        totalVerificacoes++;
        if (!condicao) {
            falhas++;
        }
        System.out.println("  [" + (condicao ? "OK" : "FALHOU") + "] " + descricao);
    }
}