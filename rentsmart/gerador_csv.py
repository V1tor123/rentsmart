"""Exportação da projeção financeira para CSV."""

import csv
from decimal import Decimal
from pathlib import Path

from .moeda import formatar_csv
from .orcamento import Orcamento


class GeradorCSV:
    """Grava a projeção de um orçamento em arquivo CSV.

    Usa ';' como separador e vírgula decimal, formato que o Excel em português
    abre corretamente com duplo clique. A codificação utf-8-sig (UTF-8 com BOM)
    faz o Excel exibir os acentos sem erro.
    """

    CABECALHO = ["mes", "aluguel", "parcela_taxa_contratual", "total_mes"]

    def __init__(self, pasta_saida: str | Path = "saida"):
        self._pasta = Path(pasta_saida)

    def gerar(self, orcamento: Orcamento, nome_arquivo: str = "projecao_12_meses.csv") -> Path:
        self._pasta.mkdir(parents=True, exist_ok=True)
        caminho = self._caminho_livre(nome_arquivo)
        projecao = orcamento.gerar_projecao()

        with open(caminho, "x", newline="", encoding="utf-8-sig") as arquivo:
            escritor = csv.writer(arquivo, delimiter=";")
            escritor.writerow(self.CABECALHO)
            for linha in projecao:
                escritor.writerow([
                    linha.mes,
                    formatar_csv(linha.aluguel),
                    formatar_csv(linha.parcela_taxa),
                    formatar_csv(linha.total),
                ])
            total_aluguel = sum((linha.aluguel for linha in projecao), Decimal("0"))
            total_taxa = sum((linha.parcela_taxa for linha in projecao), Decimal("0"))
            escritor.writerow([
                "TOTAL",
                formatar_csv(total_aluguel),
                formatar_csv(total_taxa),
                formatar_csv(total_aluguel + total_taxa),
            ])
        return caminho

    def _caminho_livre(self, nome_arquivo: str) -> Path:
        """Evita sobrescrever um CSV anterior: projecao.csv -> projecao_2.csv -> ..."""
        caminho = self._pasta / nome_arquivo
        contador = 2
        while caminho.exists():
            caminho = self._pasta / f"{Path(nome_arquivo).stem}_{contador}.csv"
            contador += 1
        return caminho
