"""Simulação de paginação com 8 quadros de 1.024 bytes, sem memória virtual."""

TAMANHO_MEMORIA = 8192
TAMANHO_PAGINA = 1024
QUANTIDADE_QUADROS = TAMANHO_MEMORIA // TAMANHO_PAGINA


def calcular_paginas(tamanho):
    """Arredonda a divisão para cima usando apenas números inteiros."""
    if tamanho <= 0:
        raise ValueError("O tamanho do processo deve ser maior que zero.")
    return (tamanho + TAMANHO_PAGINA - 1) // TAMANHO_PAGINA


def alocar_processo(pid, tamanho, memoria):
    """Aloca todas as páginas ou recusa o processo sem modificar a memória."""
    paginas = calcular_paginas(tamanho)
    processo = {
        "pid": pid,
        "tamanho": tamanho,
        "paginas": paginas,
        "alocado": False,
        "tabela": [],
        "fragmentacao": 0,
    }

    # Visita os quadros pares e depois os ímpares para demonstrar que as
    # páginas podem ocupar quadros não consecutivos. Não é substituição.
    ordem = list(range(0, len(memoria), 2)) + list(range(1, len(memoria), 2))
    livres = [quadro for quadro in ordem if memoria[quadro] is None]

    if paginas > len(livres):
        return processo

    for pagina, quadro in enumerate(livres[:paginas]):
        memoria[quadro] = (pid, pagina)
        processo["tabela"].append(quadro)

    processo["alocado"] = True
    processo["fragmentacao"] = paginas * TAMANHO_PAGINA - tamanho
    return processo


def traduzir_endereco(processo, endereco_logico):
    """Retorna página, deslocamento, quadro e endereço físico."""
    if not processo["alocado"]:
        raise ValueError("O processo não foi alocado e não possui endereço físico.")
    if not 0 <= endereco_logico < processo["tamanho"]:
        raise ValueError(
            f"Endereço inválido. Use de 0 a {processo['tamanho'] - 1}."
        )

    pagina = endereco_logico // TAMANHO_PAGINA
    deslocamento = endereco_logico % TAMANHO_PAGINA
    quadro = processo["tabela"][pagina]
    endereco_fisico = quadro * TAMANHO_PAGINA + deslocamento
    return pagina, deslocamento, quadro, endereco_fisico


def ler_inteiro(mensagem, minimo=None, maximo=None):
    """Repete a pergunta quando a entrada não é um inteiro no intervalo."""
    while True:
        try:
            valor = int(input(mensagem))
        except ValueError:
            print("Entrada inválida. Digite um número inteiro.")
            continue

        if minimo is not None and valor < minimo:
            print(f"Digite um valor maior ou igual a {minimo}.")
        elif maximo is not None and valor > maximo:
            print(f"Digite um valor menor ou igual a {maximo}.")
        else:
            return valor


def mostrar_processo(processo):
    print(f"\nProcesso P{processo['pid']}: {processo['tamanho']} bytes")
    print(f"Páginas necessárias: {processo['paginas']}")
    if not processo["alocado"]:
        print("Não pôde ser alocado: quadros livres insuficientes.")
        return

    print("Tabela de páginas (numeração iniciada em zero):")
    print("Página | Quadro")
    for pagina, quadro in enumerate(processo["tabela"]):
        print(f"{pagina:>6} | {quadro:>6}")
    print(f"Fragmentação interna: {processo['fragmentacao']} bytes")


def mostrar_resumo(memoria, processos):
    print("\n=== MEMÓRIA FÍSICA ===")
    for quadro, ocupante in enumerate(memoria):
        inicio = quadro * TAMANHO_PAGINA
        fim = inicio + TAMANHO_PAGINA - 1
        if ocupante is None:
            descricao = "livre"
        else:
            pid, pagina = ocupante
            descricao = f"P{pid}, página {pagina}"
        print(f"Quadro {quadro} | bytes {inicio:>4} a {fim:>4} | {descricao}")

    utilizados = sum(ocupante is not None for ocupante in memoria)
    fragmentacao_total = sum(p["fragmentacao"] for p in processos if p["alocado"])
    print("\n=== RESUMO ===")
    print(f"Quadros utilizados: {utilizados}")
    print(f"Quadros livres: {len(memoria) - utilizados}")
    print(f"Fragmentação interna total: {fragmentacao_total} bytes")


def main():
    memoria = [None] * QUANTIDADE_QUADROS
    processos = []

    print("=== SIMULADOR DE PAGINAÇÃO ===")
    print(f"Memória física: {TAMANHO_MEMORIA} bytes")
    print(f"Página/quadro: {TAMANHO_PAGINA} bytes")
    print(f"Quantidade de quadros: {QUANTIDADE_QUADROS}\n")
    quantidade = ler_inteiro("Quantidade de processos: ", minimo=1)

    for pid in range(1, quantidade + 1):
        tamanho = ler_inteiro(f"\nTamanho de P{pid} em bytes: ", minimo=1)
        processo = alocar_processo(pid, tamanho, memoria)
        processos.append(processo)
        mostrar_processo(processo)

    mostrar_resumo(memoria, processos)
    if not any(p["alocado"] for p in processos):
        print("\nNenhum processo alocado. Não há endereços para traduzir.")
        return

    print("\n=== TRADUÇÃO DE ENDEREÇOS ===")
    print("Informe o número do processo (ex.: 1 para P1). Use 0 para sair.")
    while True:
        pid = ler_inteiro("\nProcesso: ", minimo=0, maximo=quantidade)
        if pid == 0:
            print("Simulação encerrada.")
            break

        processo = processos[pid - 1]
        if not processo["alocado"]:
            print("Esse processo não foi alocado. Escolha outro processo.")
            continue

        endereco = ler_inteiro(
            f"Endereço lógico de P{pid} (0 a {processo['tamanho'] - 1}): ",
            minimo=0,
            maximo=processo["tamanho"] - 1,
        )
        pagina, deslocamento, quadro, fisico = traduzir_endereco(processo, endereco)
        print(f"Página: {pagina}")
        print(f"Deslocamento: {deslocamento} bytes")
        print(f"Quadro: {quadro}")
        print(f"Endereço físico: {quadro} * {TAMANHO_PAGINA} + {deslocamento} = {fisico}")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nSimulação interrompida.")
