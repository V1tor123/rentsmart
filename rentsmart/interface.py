"""Interface de terminal: coleta e valida entradas e exibe o orçamento.

Esta classe só cuida da conversa com o usuário. Os cálculos ficam nas
classes de domínio (Imovel, TaxaContratual, Orcamento), o que permite
testar as regras sem precisar digitar nada.
"""

from datetime import datetime
from pathlib import Path
from typing import Callable

from .contrato import TaxaContratual
from .gerador_csv import GeradorCSV
from .imoveis import Apartamento, Casa, Estudio, Imovel
from .moeda import formatar_moeda
from .orcamento import Orcamento

LARGURA = 60


class InterfaceTerminal:
    def __init__(self, entrada: Callable[[str], str] = input,
                 saida: Callable[[str], None] = print,
                 pasta_saida: str | Path = "saida"):
        # entrada/saida são injetáveis para que os testes simulem o usuário.
        self._entrada = entrada
        self._saida = saida
        self._gerador = GeradorCSV(pasta_saida)

    # ------------------------------------------------------------ fluxo principal
    def executar(self) -> None:
        self._saida("=" * LARGURA)
        self._saida("RentSmart - Orçamento de Locação | R.M Imóveis".center(LARGURA))
        self._saida("=" * LARGURA)
        while True:
            opcao = self.ler_opcao("\nMENU PRINCIPAL\n[1] Novo orçamento\n[0] Sair\nOpção: ",
                                   {"1", "0"})
            if opcao == "0":
                self._saida("Obrigado por usar o RentSmart. Até logo!")
                return
            self.realizar_orcamento()

    def realizar_orcamento(self) -> Orcamento:
        imovel = self.coletar_imovel()
        parcelas = self.ler_inteiro(
            f"Em quantas parcelas deseja pagar a taxa contratual de "
            f"{formatar_moeda(TaxaContratual.VALOR_TOTAL)}? "
            f"({TaxaContratual.MIN_PARCELAS} a {TaxaContratual.MAX_PARCELAS}): ",
            TaxaContratual.MIN_PARCELAS, TaxaContratual.MAX_PARCELAS)
        orcamento = Orcamento(imovel, TaxaContratual(parcelas))

        self.exibir_orcamento(orcamento)
        self.exibir_projecao(orcamento)
        self.salvar_csv(orcamento)
        return orcamento

    # ------------------------------------------------------------ coleta de dados
    def coletar_imovel(self) -> Imovel:
        tipo = self.ler_opcao("\nTipo de imóvel:\n[1] Apartamento (R$ 700,00)\n"
                              "[2] Casa (R$ 900,00)\n[3] Estúdio (R$ 1.200,00)\nOpção: ",
                              {"1", "2", "3"})
        if tipo == "3":
            return self._coletar_estudio()

        quartos = int(self.ler_opcao("Quantidade de quartos [1 ou 2]: ", {"1", "2"}))
        garagem = self.ler_sim_nao("Deseja incluir 1 vaga de garagem por R$ 300,00? (s/n): ")
        if tipo == "1":
            possui_criancas = self.ler_sim_nao("O cliente possui crianças? (s/n): ")
            return Apartamento(quartos, garagem, possui_criancas)
        return Casa(quartos, garagem)

    def _coletar_estudio(self) -> Estudio:
        self._saida("Estúdios não possuem opção de quartos adicionais.")
        garagem = self.ler_sim_nao(
            "Deseja contratar o pacote de garagem com 2 vagas por R$ 250,00? (s/n): ")
        adicionais = 0
        if garagem:
            adicionais = self.ler_inteiro(
                f"Quantas vagas ADICIONAIS (R$ 60,00 cada)? "
                f"(0 a {Estudio.MAX_VAGAS_ADICIONAIS}): ",
                0, Estudio.MAX_VAGAS_ADICIONAIS)
        return Estudio(garagem, adicionais)

    # ------------------------------------------------------------ leitura validada
    def ler_opcao(self, mensagem: str, validas: set[str]) -> str:
        while True:
            resposta = self._entrada(mensagem).strip()
            if resposta in validas:
                return resposta
            self._saida(f"Opção inválida. Digite uma destas: {', '.join(sorted(validas))}.")

    def ler_sim_nao(self, mensagem: str) -> bool:
        while True:
            resposta = self._entrada(mensagem).strip().lower()
            if resposta in ("s", "sim"):
                return True
            if resposta in ("n", "nao", "não"):
                return False
            self._saida("Resposta inválida. Digite 's' para sim ou 'n' para não.")

    def ler_inteiro(self, mensagem: str, minimo: int, maximo: int) -> int:
        while True:
            resposta = self._entrada(mensagem).strip()
            try:
                valor = int(resposta)
            except ValueError:
                self._saida("Valor inválido. Digite um número inteiro.")
                continue
            if minimo <= valor <= maximo:
                return valor
            self._saida(f"Valor fora do intervalo. Digite um número de {minimo} a {maximo}.")

    # ------------------------------------------------------------ exibição
    def _linha_valor(self, descricao: str, valor) -> None:
        self._saida(f"  {descricao:<42}{formatar_moeda(valor):>16}")

    def exibir_orcamento(self, orcamento: Orcamento) -> None:
        self._saida("\n" + "=" * LARGURA)
        self._saida("ORÇAMENTO DE LOCAÇÃO".center(LARGURA))
        self._saida("=" * LARGURA)
        self._saida(f"Imóvel: {orcamento.imovel.descrever()}")
        self._saida("-" * LARGURA)
        self._saida("ALUGUEL MENSAL")
        self._linha_valor(f"Aluguel-base ({orcamento.imovel.TIPO})", orcamento.aluguel_base)
        if orcamento.adicionais:
            for item in orcamento.adicionais:
                self._linha_valor(f"+ {item.descricao}", item.valor)
        else:
            self._saida("  (sem adicionais)")
        self._linha_valor("Subtotal com adicionais", orcamento.subtotal)
        for item in orcamento.descontos:
            self._linha_valor(f"- {item.descricao}", item.valor)
        self._linha_valor("ALUGUEL MENSAL FINAL", orcamento.aluguel_mensal)
        self._saida("-" * LARGURA)

        taxa = orcamento.taxa_contratual
        self._saida("TAXA CONTRATUAL (cobrada à parte do aluguel)")
        self._linha_valor("Valor total da taxa", taxa.valor_total)
        self._saida(f"  Parcelamento: {taxa.numero_parcelas}x")
        for numero, valor in enumerate(taxa.parcelas, start=1):
            self._linha_valor(f"Parcela {numero} (mês {numero})", valor)
        self._saida("=" * LARGURA)

    def exibir_projecao(self, orcamento: Orcamento) -> None:
        self._saida("\nPROJEÇÃO DOS 12 PRIMEIROS MESES")
        self._saida(f"  {'Mês':>3} | {'Aluguel':>14} | {'Taxa contratual':>15} | {'Total':>14}")
        for linha in orcamento.gerar_projecao():
            self._saida(f"  {linha.mes:>3} | {formatar_moeda(linha.aluguel):>14} | "
                        f"{formatar_moeda(linha.parcela_taxa):>15} | "
                        f"{formatar_moeda(linha.total):>14}")

    def salvar_csv(self, orcamento: Orcamento) -> Path | None:
        nome = f"projecao_12_meses_{datetime.now():%Y%m%d_%H%M%S}.csv"
        try:
            caminho = self._gerador.gerar(orcamento, nome)
        except OSError as erro:
            # Ex.: pasta sem permissão de escrita ou arquivo aberto em outro programa.
            self._saida(f"Não foi possível salvar o CSV: {erro}")
            return None
        self._saida(f"\nArquivo CSV gerado em: {caminho.resolve()}")
        return caminho
