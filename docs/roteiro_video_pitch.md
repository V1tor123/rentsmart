# Roteiro do vídeo pitch — RentSmart (até 4 minutos)

**Duração-alvo:** 3min50s (deixa 10s de folga para o limite de 4 minutos).
**Formato:** gravação de tela com sua voz (OBS Studio, Xbox Game Bar `Win + Alt + R`, ou o gravador do Teams/Zoom).
**Publicação:** YouTube como **Não listado**.

---

## Preparação (antes de apertar "gravar")

1. Feche notificações (Windows: *Assistente de foco / Não perturbe*).
2. No VS Code, aumente a fonte (`Ctrl + =` duas ou três vezes) e deixe abertas estas abas, nesta ordem:
   `docs/fluxograma/fluxograma_parte1.png` · `docs/fluxograma/fluxograma_parte2.png` · `docs/diagrama_classes.png` ·
   `rentsmart/imoveis.py` · `rentsmart/orcamento.py` · `rentsmart/contrato.py`
3. Abra o terminal integrado (`Ctrl + '`) na pasta do projeto e rode `cls` para limpá-lo.
4. Apague (ou deixe vazia) a pasta `saida/`, para que só o CSV do vídeo apareça nela.
5. Ensaie uma vez com cronômetro. Se passar de 4 minutos, corte frases do bloco 5 (código).

**Entradas que você vai digitar no bloco 6** (escreva num papel):
`1` → `1` → `2` → `s` → `n` → `7` *(erro proposital)* → `3` → *(mostra o orçamento)* → `0`
(apartamento, 2 quartos, garagem, sem crianças, taxa em 3x → aluguel R$ 1.140,00)

---

## Bloco 1 — Apresentação e problema · 0:00 a 0:20 (20s)

**Na tela:** a capa do relatório PDF ou o README aberto no VS Code.

**Fale:**
> "Olá, eu sou o Vitor Barioni Ferraz, RA 258824, do curso de Ciência da Computação da UNIFECAF. Este é o RentSmart, meu projeto de Algorithmic Thinking e Orientação a Objetos.
> A imobiliária R.M Imóveis calculava os orçamentos de locação na mão. Isso deixava o atendimento lento e abria espaço para erro nos adicionais, no desconto e na taxa de contrato."

## Bloco 2 — Solução proposta · 0:20 a 0:40 (20s)

**Na tela:** README, rolando até a tabela de regras comerciais.

**Fale:**
> "O RentSmart é um programa em Python, de terminal, que pergunta as características da locação, aplica as regras da imobiliária sozinho e mostra o orçamento detalhado. A taxa de contrato de dois mil reais aparece separada do aluguel e, no final, o sistema gera um CSV com os 12 primeiros meses de contrato.
> Um ponto que o enunciado não deixava claro era a garagem do estúdio. Eu defini que ela começa sempre pelo pacote de duas vagas, e as vagas extras custam sessenta reais cada."

## Bloco 3 — Fluxograma e lógica · 0:40 a 1:10 (30s)

**Na tela:** `fluxograma_parte1.png` (15s) e depois `fluxograma_parte2.png` (15s). Aponte com o mouse o que estiver falando.

**Fale:**
> "Antes de programar, montei o fluxograma. Na primeira parte, o menu leva à escolha do tipo de imóvel. Se for estúdio, o sistema pergunta da garagem em pacote. Se for casa ou apartamento, pergunta quartos e vaga, e só no apartamento pergunta se o cliente tem crianças. Cada pergunta em azul se repete até o usuário digitar um valor válido.
> Na segunda parte vem o cálculo: subtotal com os adicionais, desconto de 5% só para apartamento sem crianças, depois um laço de 12 meses que só soma a parcela da taxa nos meses do parcelamento. No final, o programa grava o CSV e volta para o menu."

## Bloco 4 — Estrutura de classes · 1:10 a 1:40 (30s)

**Na tela:** `docs/diagrama_classes.png`.

**Fale:**
> "Esta é a estrutura de classes. Imovel é uma classe abstrata, e dela saem Estudio e ImovelResidencial. ImovelResidencial guarda o que casa e apartamento têm em comum, que é o segundo quarto e a vaga de trezentos reais. Por isso a classe Casa ficou só com os seus valores.
> O Orcamento junta um imóvel com uma TaxaContratual e gera as linhas da projeção. O GeradorCSV grava o arquivo, e a InterfaceTerminal só conversa com o usuário: ela não faz nenhum cálculo."

## Bloco 5 — Principais trechos do código · 1:40 a 2:30 (50s)

**Na tela (cerca de 17s cada):**
1. `rentsmart/imoveis.py`: role até `class Apartamento` e selecione o método `calcular_descontos`.
2. `rentsmart/orcamento.py`: selecione as propriedades `subtotal`, `descontos` e `aluguel_mensal`.
3. `rentsmart/contrato.py`: selecione `_calcular_parcelas` e `parcela_do_mes`.

**Fale:**
> "Aqui no Apartamento está a regra do desconto. Ele sobrescreve calcular_descontos e devolve 5% sobre o valor que já inclui os adicionais, mas só se o cliente não tiver crianças.
> No Orcamento, repare que não tem nenhum 'se for apartamento'. Ele só pede para o imóvel calcular adicionais e descontos, e cada tipo responde do seu jeito. Isso é polimorfismo.
> Na TaxaContratual, o valor é dividido em centavos inteiros. Quando a conta não fecha, como dois mil dividido por três, os centavos que sobram vão para as primeiras parcelas, e a soma sempre dá dois mil exatos. Todo o dinheiro usa Decimal, para não ter erro de arredondamento."

## Bloco 6 — Execução de um orçamento completo · 2:30 a 3:15 (45s)

**Na tela:** terminal do VS Code. Digite `python main.py` e as entradas do papel.

**Fale (enquanto digita):**
> "Vamos rodar. Novo orçamento, apartamento, dois quartos, com garagem e cliente sem crianças. Nas parcelas vou digitar sete, que é inválido…"

*(Digite `7` e mostre a mensagem "Valor fora do intervalo"; depois digite `3`.)*

> "…o sistema avisa e pergunta de novo. Com três parcelas, fica assim: aluguel-base de setecentos, mais duzentos do quarto, mais trezentos da vaga, que dá mil e duzentos. Com o desconto de 5%, o aluguel final é mil cento e quarenta reais. A taxa aparece separada, em três parcelas de 666,67, 666,67 e 666,66. Embaixo está a projeção dos 12 meses."

*(Digite `0` para sair.)*

## Bloco 7 — Abertura do CSV · 3:15 a 3:35 (20s)

**Na tela:** no terminal, digite `start saida` e dê duplo clique no CSV, que abre no Excel. Se não tiver Excel, clique no arquivo no explorador do VS Code.

**Fale:**
> "O CSV foi gerado na pasta saida. Abrindo no Excel, estão o mês, o aluguel, a parcela da taxa e o total. A taxa só aparece nos meses 1 a 3, e a linha TOTAL mostra os dois mil reais de taxa somados no ano."

## Bloco 8 — Importância da POO e encerramento · 3:35 a 3:50 (15s)

**Na tela:** de volta ao diagrama de classes, ou o terminal com `python -m unittest discover -s tests` mostrando `OK`.

**Fale:**
> "A Orientação a Objetos deixou cada regra no seu lugar: a herança evitou código repetido, o polimorfismo deixou o orçamento funcionar para qualquer imóvel e o encapsulamento impede dados inválidos. Ainda tem 35 testes automatizados conferindo as regras. O link do repositório está na descrição. Obrigado!"

---

## Depois de gravar

1. Assista uma vez inteira e confira se o áudio está audível e se o texto do código está legível.
2. No YouTube: **Criar > Enviar vídeo**. Título sugerido: *RentSmart — Orçamento de Locação em Python com POO (UNIFECAF)*. Visibilidade **Não listado**.
3. Coloque na descrição o link do repositório do GitHub.
4. Abra o link do vídeo numa janela anônima para confirmar que ele abre sem login.
5. Cole o link no README (campo "Vídeo pitch") e no AVA.
