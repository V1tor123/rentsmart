"""Modelo dos imóveis da R.M Imóveis.

A classe abstrata Imovel define o que todo imóvel precisa saber fazer
(informar aluguel-base, adicionais e descontos). Cada subclasse implementa
apenas as regras comerciais que são exclusivas do seu tipo.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal

from .moeda import arredondar


@dataclass(frozen=True)
class ItemOrcamento:
    """Uma linha do orçamento: um adicional (valor positivo) ou um desconto (negativo)."""

    descricao: str
    valor: Decimal


class Imovel(ABC):
    """Classe base de todos os imóveis. Não pode ser instanciada diretamente."""

    TIPO = "Imóvel"
    ALUGUEL_BASE = Decimal("0.00")

    def __init__(self, quartos: int = 1):
        self._quartos = self._validar_quartos(quartos)

    @property
    def quartos(self) -> int:
        return self._quartos

    @property
    def aluguel_base(self) -> Decimal:
        return self.ALUGUEL_BASE

    @staticmethod
    def _validar_quartos(quartos: int) -> int:
        if quartos not in (1, 2):
            raise ValueError("A quantidade de quartos deve ser 1 ou 2.")
        return quartos

    @abstractmethod
    def calcular_adicionais(self) -> list[ItemOrcamento]:
        """Retorna a lista de adicionais mensais do imóvel."""

    def calcular_descontos(self, valor_com_adicionais: Decimal) -> list[ItemOrcamento]:
        """Por padrão um imóvel não tem descontos. Subclasses podem sobrescrever."""
        return []

    @abstractmethod
    def descrever(self) -> str:
        """Texto curto com as características escolhidas."""


class ImovelResidencial(Imovel):
    """Base comum de Casa e Apartamento.

    Os dois tipos compartilham a mesma estrutura de regras: opção de segundo
    quarto (valor diferente em cada subclasse) e uma única vaga de garagem
    por R$ 300,00. Centralizar isso aqui evita repetir código.
    """

    ADICIONAL_SEGUNDO_QUARTO = Decimal("0.00")
    VALOR_VAGA = Decimal("300.00")

    def __init__(self, quartos: int = 1, possui_garagem: bool = False):
        super().__init__(quartos)
        self._possui_garagem = bool(possui_garagem)

    @property
    def possui_garagem(self) -> bool:
        return self._possui_garagem

    def calcular_adicionais(self) -> list[ItemOrcamento]:
        adicionais = []
        if self.quartos == 2:
            adicionais.append(ItemOrcamento("Segundo quarto", self.ADICIONAL_SEGUNDO_QUARTO))
        if self.possui_garagem:
            adicionais.append(ItemOrcamento("Vaga de garagem (1 vaga)", self.VALOR_VAGA))
        return adicionais

    def descrever(self) -> str:
        garagem = "com 1 vaga de garagem" if self.possui_garagem else "sem garagem"
        return f"{self.TIPO} com {self.quartos} quarto(s), {garagem}"


class Apartamento(ImovelResidencial):
    TIPO = "Apartamento"
    ALUGUEL_BASE = Decimal("700.00")
    ADICIONAL_SEGUNDO_QUARTO = Decimal("200.00")
    PERCENTUAL_DESCONTO_SEM_CRIANCAS = Decimal("0.05")

    def __init__(self, quartos: int = 1, possui_garagem: bool = False,
                 possui_criancas: bool = True):
        super().__init__(quartos, possui_garagem)
        self._possui_criancas = bool(possui_criancas)

    @property
    def possui_criancas(self) -> bool:
        return self._possui_criancas

    def calcular_descontos(self, valor_com_adicionais: Decimal) -> list[ItemOrcamento]:
        # Regra: 5% sobre o aluguel já somado aos adicionais, só para quem não tem crianças.
        if self.possui_criancas:
            return []
        desconto = arredondar(valor_com_adicionais * self.PERCENTUAL_DESCONTO_SEM_CRIANCAS)
        return [ItemOrcamento("Desconto de 5% (cliente sem crianças)", -desconto)]

    def descrever(self) -> str:
        criancas = "possui crianças" if self.possui_criancas else "não possui crianças"
        return f"{super().descrever()}; cliente {criancas}"


class Casa(ImovelResidencial):
    TIPO = "Casa"
    ALUGUEL_BASE = Decimal("900.00")
    ADICIONAL_SEGUNDO_QUARTO = Decimal("250.00")


class Estudio(Imovel):
    """Estúdio: sem opção de quartos; garagem contratada em pacote de 2 vagas.

    Interpretação adotada (o enunciado não detalha):
    - o cliente pode não contratar garagem (0 vagas);
    - se contratar, recebe o pacote inicial de 2 vagas por R$ 250,00;
    - cada vaga além das 2 do pacote custa R$ 60,00;
    - não existe vaga avulsa: quem precisa de apenas 1 vaga contrata o pacote.
    """

    TIPO = "Estúdio"
    ALUGUEL_BASE = Decimal("1200.00")
    VAGAS_NO_PACOTE = 2
    VALOR_PACOTE = Decimal("250.00")
    VALOR_VAGA_ADICIONAL = Decimal("60.00")
    MAX_VAGAS_ADICIONAIS = 8  # limite operacional adotado: até 10 vagas no total

    def __init__(self, contratar_garagem: bool = False, vagas_adicionais: int = 0):
        super().__init__(quartos=1)
        if not contratar_garagem and vagas_adicionais:
            raise ValueError("Vagas adicionais exigem a contratação do pacote de garagem.")
        if not 0 <= vagas_adicionais <= self.MAX_VAGAS_ADICIONAIS:
            raise ValueError(
                f"As vagas adicionais devem estar entre 0 e {self.MAX_VAGAS_ADICIONAIS}."
            )
        self._contratar_garagem = bool(contratar_garagem)
        self._vagas_adicionais = vagas_adicionais

    @property
    def contratar_garagem(self) -> bool:
        return self._contratar_garagem

    @property
    def vagas_adicionais(self) -> int:
        return self._vagas_adicionais

    @property
    def total_vagas(self) -> int:
        if not self.contratar_garagem:
            return 0
        return self.VAGAS_NO_PACOTE + self.vagas_adicionais

    def calcular_adicionais(self) -> list[ItemOrcamento]:
        adicionais = []
        if self.contratar_garagem:
            adicionais.append(ItemOrcamento("Pacote de garagem (2 vagas)", self.VALOR_PACOTE))
        if self.vagas_adicionais:
            valor = self.VALOR_VAGA_ADICIONAL * self.vagas_adicionais
            adicionais.append(ItemOrcamento(
                f"Vagas adicionais ({self.vagas_adicionais} x R$ 60,00)", valor))
        return adicionais

    def descrever(self) -> str:
        if self.total_vagas == 0:
            return "Estúdio sem garagem"
        return f"Estúdio com {self.total_vagas} vagas de garagem"
