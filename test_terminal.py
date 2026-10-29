"""Executa o programa completo com entradas simuladas, sem pacotes externos."""

from pathlib import Path
import os
import subprocess
import sys
import unittest


PASTA = Path(__file__).resolve().parent


class TestTerminal(unittest.TestCase):
    def executar(self, entradas):
        resultado = subprocess.run(
            [sys.executable, str(PASTA / "paginacao.py")],
            input=entradas,
            text=True,
            encoding="utf-8",
            capture_output=True,
            cwd=PASTA,
            timeout=5,
            # Mantém os acentos iguais no Windows, Linux e macOS.
            env=dict(os.environ, PYTHONIOENCODING="utf-8"),
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(resultado.stderr, "")
        return resultado.stdout

    def conferir(self, saida, *trechos):
        for trecho in trechos:
            self.assertIn(trecho, saida)

    def test_nenhum_processo_alocado(self):
        saida = self.executar("2\n8193\n9000\n")
        self.conferir(
            saida, "Quadros utilizados: 0", "Quadros livres: 8",
            "Fragmentação interna total: 0 bytes", "Nenhum processo alocado.",
        )
        self.assertNotIn("=== TRADUÇÃO DE ENDEREÇOS ===", saida)
        self.assertEqual(saida.count("Não pôde ser alocado:"), 2)

    def test_oito_processos_de_um_byte_e_recusa_do_nono(self):
        saida = self.executar("9\n" + "1\n" * 9 + "8\n0\n0\n")
        self.conferir(
            saida, "Quadros utilizados: 8", "Quadros livres: 0",
            "Fragmentação interna total: 8184 bytes", "7 * 1024 + 0 = 7168",
        )
        self.assertEqual(saida.count("Não pôde ser alocado:"), 1)

    def test_oito_processos_sem_fragmentacao(self):
        saida = self.executar("8\n" + "1024\n" * 8 + "8\n1023\n0\n")
        self.conferir(
            saida, "Quadros utilizados: 8", "Quadros livres: 0",
            "Fragmentação interna total: 0 bytes", "7 * 1024 + 1023 = 8191",
        )

    def test_entradas_invalidas_e_nova_tentativa(self):
        saida = self.executar(
            "abc\n0\n1\n-1\n0\n1.5\n1025\n-2\n2\n1\nabc\n-1\n1025\n1024\n0\n"
        )
        self.conferir(
            saida, "Entrada inválida. Digite um número inteiro.",
            "Digite um valor maior ou igual a 1.",
            "Digite um valor maior ou igual a 0.",
            "Digite um valor menor ou igual a 1.",
            "Digite um valor menor ou igual a 1024.",
            "Fragmentação interna total: 1023 bytes",
            "2 * 1024 + 0 = 2048", "Simulação encerrada.",
        )
        self.assertEqual(saida.count("Entrada inválida."), 3)
        self.assertEqual(saida.count("Endereço físico:"), 1)

    def test_recusa_e_alocacao_do_proximo_processo(self):
        saida = self.executar("3\n6144\n2500\n2048\n2\n3\n2047\n0\n")
        self.conferir(
            saida, "Quadros utilizados: 8", "Quadros livres: 0",
            "Fragmentação interna total: 0 bytes",
            "Esse processo não foi alocado. Escolha outro processo.",
            "7 * 1024 + 1023 = 8191", "Simulação encerrada.",
        )
        self.assertEqual(saida.count("Não pôde ser alocado:"), 1)

    def test_fim_da_entrada_sem_traceback(self):
        for entradas in ["", "1\n", "1\n2500\n1\n"]:
            with self.subTest(entradas=entradas):
                self.assertIn("Simulação interrompida.", self.executar(entradas))

    def test_exemplo_documentado(self):
        entradas = (PASTA / "entradas_exemplo.txt").read_text(encoding="utf-8")
        saida = self.executar(entradas)
        self.conferir(
            saida, "Quadros utilizados: 7", "Quadros livres: 1",
            "Fragmentação interna total: 1120 bytes",
            "4 * 1024 + 252 = 4348", "5 * 1024 + 475 = 5595",
            "Simulação encerrada.",
        )


if __name__ == "__main__":
    unittest.main()
