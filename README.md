# Simulador de paginação

Trabalho de gerenciamento de memória em Python. O programa distribui as páginas dos processos em uma memória física de **8.192 bytes**, dividida em **8 quadros de 1.024 bytes**, e traduz endereços lógicos para físicos usando uma tabela de páginas por processo.

## Como executar

É necessário ter Python 3 instalado. O projeto usa apenas a biblioteca padrão, sem pacotes adicionais.

No terminal, dentro da pasta do projeto:

```bash
python3 paginacao.py
```

No Windows, também é possível usar:

```powershell
py paginacao.py
```

Informe a quantidade de processos e o tamanho de cada um em bytes. Depois da alocação, escolha o número de um processo e o endereço lógico que deseja consultar. É possível fazer várias consultas; digite `0` na escolha do processo para encerrar.

## O que o programa faz

- Calcula quantas páginas cada processo precisa.
- Verifica se há espaço para todas as páginas antes de alocar.
- Mostra a tabela de páginas e a fragmentação interna de cada processo alocado.
- Informa quando um processo não cabe e continua tentando os próximos.
- Exibe a ocupação dos oito quadros e o resumo da memória.
- Traduz endereços lógicos, validando o processo e os limites do endereço.

Não há memória virtual, falta de página, substituição ou desalocação. Os processos são atendidos na ordem em que são informados. Um processo recusado não ocupa quadros e não entra na fragmentação interna total.

## Como os cálculos funcionam

### Quantidade de páginas

A divisão é arredondada para cima, pois qualquer sobra exige mais uma página:

```python
paginas = (tamanho + 1023) // 1024
```

Um processo de 2.500 bytes precisa de 3 páginas. Um de 2.048 bytes precisa de exatamente 2.

### Tabela de páginas e quadros

Página é uma divisão do espaço lógico do processo; quadro é uma divisão da memória física. Ambos têm 1.024 bytes nesta simulação. Páginas e quadros são numerados a partir de zero; os processos recebem os identificadores P1, P2, etc.

A memória é uma lista de oito posições. Cada posição guarda `(processo, página)` ou `None` quando está livre. A tabela de cada processo é outra lista: o índice é a página e o valor é o quadro correspondente.

Para deixar a alocação não contígua visível, o programa procura quadros livres na ordem **0, 2, 4, 6, 1, 3, 5, 7**. Essa é somente uma escolha didática de alocação, não um algoritmo de substituição. Alocar em quadros consecutivos também seria permitido pelo enunciado.

Por exemplo, a tabela `[0, 2, 4]` significa:

| Página lógica | Quadro físico |
| --- | --- |
| 0 | 0 |
| 1 | 2 |
| 2 | 4 |

### Fragmentação interna

```python
fragmentacao = paginas * 1024 - tamanho
```

Para 2.500 bytes: `3 * 1024 - 2500 = 572 bytes`. Essa sobra fica dentro do último quadro reservado ao processo e não pode ser usada por outro processo. Se o tamanho for múltiplo de 1.024, a fragmentação é zero.

### Tradução de endereços

```python
pagina = endereco_logico // 1024
deslocamento = endereco_logico % 1024
quadro = tabela[pagina]
endereco_fisico = quadro * 1024 + deslocamento
```

Para P1 com 2.500 bytes, tabela `[0, 2, 4]` e endereço lógico **2.300**:

| Etapa | Resultado |
| --- | --- |
| Página: `2300 // 1024` | 2 |
| Deslocamento: `2300 % 1024` | 252 bytes |
| Quadro: `tabela[2]` | 4 |
| Endereço físico: `4 * 1024 + 252` | **4.348** |

Como a contagem começa em zero, um processo de N bytes aceita endereços de **0 até N − 1**. Portanto, o endereço 2.500 é inválido para um processo de 2.500 bytes, mesmo que exista espaço de fragmentação no último quadro.

## Execução de exemplo

O arquivo [execucao.txt](execucao.txt) contém uma captura real do programa com entradas e saídas, incluindo tentativas inválidas e traduções. Os tamanhos usados foram:

| Processo | Tamanho | Páginas necessárias | Resultado | Fragmentação interna |
| --- | --- | --- | --- | --- |
| P1 | 2.500 bytes | 3 | Alocado nos quadros 0, 2 e 4 | 572 bytes |
| P2 | 2.048 bytes | 2 | Alocado nos quadros 6 e 1 | 0 bytes |
| P3 | 4.000 bytes | 4 | Recusado: restam apenas 3 quadros | Não se aplica |
| P4 | 1.500 bytes | 2 | Alocado nos quadros 3 e 5 | 548 bytes |

Resultado: **7 quadros utilizados, 1 livre e 1.120 bytes de fragmentação interna total**.

O arquivo [entradas_exemplo.txt](entradas_exemplo.txt) guarda as entradas dessa execução. No Linux/macOS, é possível reproduzir a saída com:

```bash
python3 paginacao.py < entradas_exemplo.txt
```

O redirecionamento acima não exibe os valores digitados; a captura em `execucao.txt` inclui o eco das entradas de um terminal.

## Verificação

Execute os testes com:

```bash
python3 -m unittest -v
```

No Windows, substitua `python3` por `py`. Os testes verificam arredondamento, fragmentação, memória cheia, recusa sem alocação parcial, continuidade após recusa, tabelas e limites da tradução.