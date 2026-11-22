"""Taxa contratual e seu parcelamento."""

from decimal import Decimal

from .moeda import CENTAVO


class TaxaContratual:
    """Taxa fixa de R$ 2.000,00, parcelável de 1 a 5 vezes.

    Fica separada do aluguel porque é um custo diferente: só existe nos
    primeiros meses do contrato, enquanto o aluguel se repete todo mês.
    """

    VALOR_TOTAL = Decimal("2000.00")
    MIN_PARCELAS = 1
    MAX_PARCELAS = 5

    def __init__(self, numero_parcelas: int):
        if not isinstance(numero_parcelas, int) or isinstance(numero_parcelas, bool):
            raise TypeError("O número de parcelas deve ser um número inteiro.")
        if not self.MIN_PARCELAS <= numero_parcelas <= self.MAX_PARCELAS:
            raise ValueError(
                f"O número de parcelas deve estar entre {self.MIN_PARCELAS} e {self.MAX_PARCELAS}."
            )
        self._numero_parcelas = numero_parcelas
        self._parcelas = self._calcular_parcelas()

    @property
    def numero_parcelas(self) -> int:
        return self._numero_parcelas

    @property
    def valor_total(self) -> Decimal:
        return self.VALOR_TOTAL

    @property
    def parcelas(self) -> list[Decimal]:
        return list(self._parcelas)  # cópia: quem lê não altera o estado interno

    def _calcular_parcelas(self) -> list[Decimal]:
        """Divide o total em parcelas com centavos exatos.

        Trabalha em centavos inteiros: divide o total pelo número de parcelas
        e distribui os centavos que sobram, um a um, nas primeiras parcelas.
        Ex.: 2000 / 3 -> 666,67 + 666,67 + 666,66 = 2.000,00 (soma sempre exata).
        """
        n = self._numero_parcelas
        total_centavos = int(self.VALOR_TOTAL * 100)
        base, resto = divmod(total_centavos, n)
        centavos = [base + 1 if i < resto else base for i in range(n)]
        return [(Decimal(c) / 100).quantize(CENTAVO) for c in centavos]

    def parcela_do_mes(self, mes: int) -> Decimal:
        """Valor da taxa no mês informado (1 = primeiro mês); zero fora do parcelamento."""
        if mes < 1:
            raise ValueError("O mês deve ser maior ou igual a 1.")
        if mes <= self._numero_parcelas:
            return self._parcelas[mes - 1]
        return Decimal("0.00")
