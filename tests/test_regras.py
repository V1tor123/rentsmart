"""Testes das regras comerciais do RentSmart.

Execute na raiz do projeto:  python -m unittest discover -s tests -v
"""

import csv
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rentsmart.contrato import TaxaContratual  # noqa: E402
from rentsmart.gerador_csv import GeradorCSV  # noqa: E402
from rentsmart.imoveis import Apartamento, Casa, Estudio, Imovel  # noqa: E402
from rentsmart.interface import InterfaceTerminal  # noqa: E402
from rentsmart.moeda import formatar_csv, formatar_moeda  # noqa: E402
from rentsmart.orcamento import Orcamento  # noqa: E402

D = Decimal


def aluguel(imovel, parcelas=1):
    return Orcamento(imovel, TaxaContratual(parcelas)).aluguel_mensal


class TestApartamento(unittest.TestCase):
    def test_base_sem_adicionais_com_criancas(self):
        self.assertEqual(aluguel(Apartamento(1, False, possui_criancas=True)), D("700.00"))

    def test_segundo_quarto(self):
        self.assertEqual(aluguel(Apartamento(2, False, possui_criancas=True)), D("900.00"))

    def test_garagem(self):
        self.assertEqual(aluguel(Apartamento(1, True, possui_criancas=True)), D("1000.00"))

    def test_dois_quartos_e_garagem(self):
        self.assertEqual(aluguel(Apartamento(2, True, possui_criancas=True)), D("1200.00"))

    def test_desconto_sem_criancas_sem_adicionais(self):
        self.assertEqual(aluguel(Apartamento(1, False, possui_criancas=False)), D("665.00"))

    def test_desconto_aplicado_depois_dos_adicionais(self):
        # (700 + 200 + 300) * 0,95 = 1140,00
        orc = Orcamento(Apartamento(2, True, possui_criancas=False), TaxaContratual(1))
        self.assertEqual(orc.subtotal, D("1200.00"))
        self.assertEqual(orc.total_descontos, D("-60.00"))
        self.assertEqual(orc.aluguel_mensal, D("1140.00"))

    def test_desconto_dois_quartos_sem_garagem(self):
        self.assertEqual(aluguel(Apartamento(2, False, possui_criancas=False)), D("855.00"))

    def test_sem_desconto_quando_ha_criancas(self):
        orc = Orcamento(Apartamento(2, True, possui_criancas=True), TaxaContratual(1))
        self.assertEqual(orc.descontos, [])


class TestCasa(unittest.TestCase):
    def test_base(self):
        self.assertEqual(aluguel(Casa(1, False)), D("900.00"))

    def test_segundo_quarto(self):
        self.assertEqual(aluguel(Casa(2, False)), D("1150.00"))

    def test_garagem(self):
        self.assertEqual(aluguel(Casa(1, True)), D("1200.00"))

    def test_dois_quartos_e_garagem(self):
        self.assertEqual(aluguel(Casa(2, True)), D("1450.00"))

    def test_casa_nunca_tem_desconto(self):
        orc = Orcamento(Casa(2, True), TaxaContratual(1))
        self.assertEqual(orc.descontos, [])


class TestEstudio(unittest.TestCase):
    def test_base_sem_garagem(self):
        self.assertEqual(aluguel(Estudio()), D("1200.00"))
        self.assertEqual(Estudio().total_vagas, 0)

    def test_pacote_duas_vagas(self):
        estudio = Estudio(contratar_garagem=True)
        self.assertEqual(aluguel(estudio), D("1450.00"))
        self.assertEqual(estudio.total_vagas, 2)

    def test_pacote_com_vagas_adicionais(self):
        # 1200 + 250 + 3 * 60 = 1630
        estudio = Estudio(contratar_garagem=True, vagas_adicionais=3)
        self.assertEqual(aluguel(estudio), D("1630.00"))
        self.assertEqual(estudio.total_vagas, 5)

    def test_limite_maximo_de_vagas_adicionais(self):
        self.assertEqual(aluguel(Estudio(True, 8)), D("1930.00"))
        with self.assertRaises(ValueError):
            Estudio(True, 9)

    def test_vagas_adicionais_exigem_pacote(self):
        with self.assertRaises(ValueError):
            Estudio(contratar_garagem=False, vagas_adicionais=1)

    def test_vagas_adicionais_negativas(self):
        with self.assertRaises(ValueError):
            Estudio(True, -1)

    def test_estudio_nao_tem_desconto(self):
        self.assertEqual(Orcamento(Estudio(True, 2), TaxaContratual(1)).descontos, [])


class TestValidacoesImovel(unittest.TestCase):
    def test_quartos_invalidos(self):
        for quartos in (0, 3, -1):
            with self.assertRaises(ValueError):
                Apartamento(quartos)
            with self.assertRaises(ValueError):
                Casa(quartos)

    def test_imovel_e_abstrato(self):
        with self.assertRaises(TypeError):
            Imovel()  # type: ignore[abstract]


class TestTaxaContratual(unittest.TestCase):
    def test_parcelamentos_exatos(self):
        esperado = {
            1: [D("2000.00")],
            2: [D("1000.00")] * 2,
            4: [D("500.00")] * 4,
            5: [D("400.00")] * 5,
        }
        for n, parcelas in esperado.items():
            self.assertEqual(TaxaContratual(n).parcelas, parcelas)

    def test_tres_parcelas_soma_exata(self):
        parcelas = TaxaContratual(3).parcelas
        self.assertEqual(parcelas, [D("666.67"), D("666.67"), D("666.66")])
        self.assertEqual(sum(parcelas), D("2000.00"))

    def test_soma_sempre_igual_ao_total(self):
        for n in range(1, 6):
            self.assertEqual(sum(TaxaContratual(n).parcelas), D("2000.00"))

    def test_parcelas_fora_do_intervalo(self):
        for n in (0, 6, -2, 12):
            with self.assertRaises(ValueError):
                TaxaContratual(n)

    def test_parcelas_tipo_invalido(self):
        for valor in ("3", 2.5, True):
            with self.assertRaises(TypeError):
                TaxaContratual(valor)  # type: ignore[arg-type]

    def test_parcela_do_mes(self):
        taxa = TaxaContratual(3)
        self.assertEqual(taxa.parcela_do_mes(1), D("666.67"))
        self.assertEqual(taxa.parcela_do_mes(3), D("666.66"))
        self.assertEqual(taxa.parcela_do_mes(4), D("0.00"))
        with self.assertRaises(ValueError):
            taxa.parcela_do_mes(0)


class TestProjecao(unittest.TestCase):
    def test_doze_meses_com_taxa_apenas_nos_meses_parcelados(self):
        orc = Orcamento(Apartamento(2, True, possui_criancas=False), TaxaContratual(4))
        projecao = orc.gerar_projecao()
        self.assertEqual(len(projecao), 12)
        self.assertEqual([linha.mes for linha in projecao], list(range(1, 13)))
        for linha in projecao:
            self.assertEqual(linha.aluguel, D("1140.00"))
            esperado_taxa = D("500.00") if linha.mes <= 4 else D("0.00")
            self.assertEqual(linha.parcela_taxa, esperado_taxa)
            self.assertEqual(linha.total, linha.aluguel + linha.parcela_taxa)
        self.assertEqual(sum(linha.parcela_taxa for linha in projecao), D("2000.00"))

    def test_projecao_com_taxa_a_vista(self):
        projecao = Orcamento(Casa(1, False), TaxaContratual(1)).gerar_projecao()
        self.assertEqual(projecao[0].total, D("2900.00"))
        self.assertTrue(all(linha.total == D("900.00") for linha in projecao[1:]))


class TestGeradorCSV(unittest.TestCase):
    def test_conteudo_do_csv(self):
        orc = Orcamento(Estudio(True, 1), TaxaContratual(3))  # aluguel 1510,00
        with tempfile.TemporaryDirectory() as pasta:
            caminho = GeradorCSV(pasta).gerar(orc, "teste.csv")
            with open(caminho, encoding="utf-8-sig", newline="") as arquivo:
                linhas = list(csv.reader(arquivo, delimiter=";"))

        self.assertEqual(linhas[0], ["mes", "aluguel", "parcela_taxa_contratual", "total_mes"])
        self.assertEqual(len(linhas), 14)  # cabeçalho + 12 meses + total
        self.assertEqual(linhas[1], ["1", "1510,00", "666,67", "2176,67"])
        self.assertEqual(linhas[3], ["3", "1510,00", "666,66", "2176,66"])
        self.assertEqual(linhas[4], ["4", "1510,00", "0,00", "1510,00"])
        self.assertEqual(linhas[13], ["TOTAL", "18120,00", "2000,00", "20120,00"])


class TestMoeda(unittest.TestCase):
    def test_formatacao(self):
        self.assertEqual(formatar_moeda(D("1234.5")), "R$ 1.234,50")
        self.assertEqual(formatar_moeda(D("665")), "R$ 665,00")
        self.assertEqual(formatar_moeda(D("-60")), "-R$ 60,00")
        self.assertEqual(formatar_csv(D("1140")), "1140,00")


class TestInterface(unittest.TestCase):
    """Simula um usuário digitando, inclusive respostas inválidas."""

    def executar(self, respostas):
        entradas = iter(respostas)
        saidas = []
        with tempfile.TemporaryDirectory() as pasta:
            ui = InterfaceTerminal(entrada=lambda _msg: next(entradas),
                                   saida=saidas.append, pasta_saida=pasta)
            ui.executar()
            arquivos = list(Path(pasta).glob("*.csv"))
        return "\n".join(saidas), arquivos

    def test_fluxo_completo_com_entradas_invalidas(self):
        respostas = [
            "9", "1",         # menu: inválido, depois novo orçamento
            "x", "1",         # tipo: inválido, depois apartamento
            "3", "2",         # quartos: inválido, depois 2
            "talvez", "s",    # garagem: inválido, depois sim
            "n",              # possui crianças? não -> desconto de 5%
            "abc", "7", "3",  # parcelas: texto, fora do intervalo, depois 3
            "0",              # sair
        ]
        texto, arquivos = self.executar(respostas)
        self.assertIn("Opção inválida", texto)
        self.assertIn("Resposta inválida", texto)
        self.assertIn("Valor inválido", texto)
        self.assertIn("Valor fora do intervalo", texto)
        self.assertIn("R$ 1.140,00", texto)
        self.assertIn("R$ 666,67", texto)
        self.assertEqual(len(arquivos), 1)

    def test_estudio_pelo_terminal(self):
        respostas = ["1", "3", "s", "2", "1", "0"]  # estúdio, pacote, +2 vagas, à vista
        texto, arquivos = self.executar(respostas)
        self.assertIn("R$ 1.570,00", texto)  # 1200 + 250 + 2 * 60
        self.assertEqual(len(arquivos), 1)

    def test_dois_orcamentos_seguidos_geram_dois_csv(self):
        respostas = ["1", "2", "1", "n", "1",        # casa 1 quarto, sem garagem, à vista
                     "1", "2", "2", "s", "5", "0"]   # casa 2 quartos, garagem, 5x
        texto, arquivos = self.executar(respostas)
        self.assertIn("R$ 900,00", texto)
        self.assertIn("R$ 1.450,00", texto)
        self.assertEqual(len(arquivos), 2)


if __name__ == "__main__":
    unittest.main()
