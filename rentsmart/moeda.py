"""Utilitários para valores monetários com Decimal."""

from decimal import Decimal, ROUND_HALF_UP

CENTAVO = Decimal("0.01")


def arredondar(valor: Decimal) -> Decimal:
    """Arredonda um valor para centavos (meio para cima, como em cálculos comerciais)."""
    return Decimal(valor).quantize(CENTAVO, rounding=ROUND_HALF_UP)


def formatar_moeda(valor: Decimal) -> str:
    """Formata no padrão brasileiro: Decimal('1234.5') -> 'R$ 1.234,50'."""
    valor = arredondar(valor)
    sinal = "-" if valor < 0 else ""
    texto = f"{abs(valor):,.2f}"  # '1,234.50'
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{sinal}R$ {texto}"


def formatar_csv(valor: Decimal) -> str:
    """Formato do CSV: vírgula decimal e sem separador de milhar ('1234,50')."""
    return f"{arredondar(valor):.2f}".replace(".", ",")
