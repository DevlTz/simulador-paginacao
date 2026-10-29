"""Verifica cálculos, limites e preservação da memória após recusa."""

import unittest

from paginacao import alocar_processo, calcular_paginas, traduzir_endereco


class TestPaginacao(unittest.TestCase):
    def setUp(self):
        self.memoria = [None] * 8

    def test_arredondamento(self):
        for tamanho, esperado in [(1, 1), (1024, 1), (1025, 2), (2500, 3), (8192, 8)]:
            with self.subTest(tamanho=tamanho):
                self.assertEqual(calcular_paginas(tamanho), esperado)

    def test_tamanho_invalido(self):
        for tamanho in [0, -1]:
            with self.assertRaises(ValueError):
                calcular_paginas(tamanho)

    def test_exemplo_enunciado(self):
        p = alocar_processo(1, 2500, self.memoria)
        self.assertEqual(p["tabela"], [0, 2, 4])
        self.assertEqual(p["fragmentacao"], 572)
        self.assertEqual(self.memoria[4], (1, 2))

    def test_memoria_completa_sem_fragmentacao(self):
        p = alocar_processo(1, 8192, self.memoria)
        self.assertTrue(p["alocado"])
        self.assertEqual(p["fragmentacao"], 0)
        self.assertEqual(set(p["tabela"]), set(range(8)))
        self.assertFalse(alocar_processo(2, 1, self.memoria)["alocado"])

    def test_recusa_sem_alocacao_parcial_e_continuidade(self):
        alocar_processo(1, 6144, self.memoria)
        antes = self.memoria.copy()
        recusado = alocar_processo(2, 2500, self.memoria)
        self.assertFalse(recusado["alocado"])
        self.assertEqual(recusado["tabela"], [])
        self.assertEqual(recusado["fragmentacao"], 0)
        self.assertEqual(self.memoria, antes)
        self.assertTrue(alocar_processo(3, 2048, self.memoria)["alocado"])

    def test_processo_maior_que_memoria(self):
        self.assertFalse(alocar_processo(1, 8193, self.memoria)["alocado"])
        self.assertEqual(self.memoria, [None] * 8)

    def test_traducao_e_limites_de_pagina(self):
        p = alocar_processo(1, 2500, self.memoria)
        casos = {
            0: (0, 0, 0, 0),
            1023: (0, 1023, 0, 1023),
            1024: (1, 0, 2, 2048),
            2300: (2, 252, 4, 4348),
            2499: (2, 451, 4, 4547),
        }
        for endereco, esperado in casos.items():
            with self.subTest(endereco=endereco):
                self.assertEqual(traduzir_endereco(p, endereco), esperado)

    def test_rejeita_enderecos_fora_do_processo(self):
        p = alocar_processo(1, 2500, self.memoria)
        for endereco in [-1, 2500, 3071]:
            with self.assertRaises(ValueError):
                traduzir_endereco(p, endereco)

    def test_rejeita_traducao_de_processo_nao_alocado(self):
        p = alocar_processo(1, 9000, self.memoria)
        with self.assertRaises(ValueError):
            traduzir_endereco(p, 0)

    def test_cenario_demonstracao(self):
        processos = [
            alocar_processo(pid, tamanho, self.memoria)
            for pid, tamanho in enumerate([2500, 2048, 4000, 1500], start=1)
        ]
        self.assertEqual(sum(x is not None for x in self.memoria), 7)
        self.assertEqual(sum(p["fragmentacao"] for p in processos), 1120)
        self.assertEqual(processos[3]["tabela"], [3, 5])


if __name__ == "__main__":
    unittest.main()
