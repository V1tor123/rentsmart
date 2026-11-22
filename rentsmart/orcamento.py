"""Orçamento de locação e projeção financeira dos 12 primeiros meses."""

from dataclasses import dataclass
from decimal import Decimal

from .contrato import TaxaContratual
from .imoveis import Imovel, ItemOrcamento


@dataclass(frozen=True)
class LinhaProjecao:
    """Valores previstos para um mês do contrato."""

    mes: int
    aluguel: Decimal
    parcela_taxa: Decimal

    @property
    def total(self) -> Decimal:
        return self.aluguel + self.parcela_taxa


class Orcamento:
    """Junta um imóvel e uma taxa contratual e calcula o orçamento completo.

    O Orcamento não conhece as regras de cada tipo de imóvel: ele apenas pede
    ao objeto Imovel seus adicionais e descontos (polimorfismo). Assim, um novo
    tipo de imóvel pode ser criado sem alterar esta classe.
    """

    MESES_PROJECAO = 12

    def __init__(self, imovel: Imovel, taxa_contratual: TaxaContratual):
        self._imovel = imovel
        self._taxa = taxa_contratual

    @property
    def imovel(self) -> Imovel:
        return self._imovel

    @property
    def taxa_contratual(self) -> TaxaContratual:
        return self._taxa

    @property
    def aluguel_base(self) -> Decimal:
        return self._imovel.aluguel_base

    @property
    def adicionais(self) -> list[ItemOrcamento]:
        return self._imovel.calcular_adicionais()

    @property
    def total_adicionais(self) -> Decimal:
        return sum((item.valor for item in self.adicionais), Decimal("0.00"))

    @property
    def subtotal(self) -> Decimal:
        """Aluguel-base + adicionais, antes dos descontos."""
        return self.aluguel_base + self.total_adicionais

    @property
    def descontos(self) -> list[ItemOrcamento]:
        # O desconto é calculado sobre o subtotal, ou seja, depois dos adicionais.
        return self._imovel.calcular_descontos(self.subtotal)

    @property
    def total_descontos(self) -> Decimal:
        return sum((item.valor for item in self.descontos), Decimal("0.00"))

    @property
    def aluguel_mensal(self) -> Decimal:
        return self.subtotal + self.total_descontos

    def gerar_projecao(self, meses: int = MESES_PROJECAO) -> list[LinhaProjecao]:
        """Gera uma linha por mês: o aluguel se repete; a taxa só aparece nos meses parcelados."""
        return [
            LinhaProjecao(mes, self.aluguel_mensal, self._taxa.parcela_do_mes(mes))
            for mes in range(1, meses + 1)
        ]
