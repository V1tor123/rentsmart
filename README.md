# RentSmart — Sistema de Orçamento de Locação com Python e Orientação a Objetos

Trabalho da disciplina **Algorithmic Thinking & Introduction to Object-Oriented Programming** — UNIFECAF
Aluno: **Vitor Barioni Ferraz** · RA **258824** · Ciência da Computação · 2º semestre

Aplicação de terminal que automatiza os orçamentos de locação da imobiliária fictícia **R.M Imóveis**
(apartamentos, casas e estúdios): calcula adicionais e descontos, apresenta o orçamento detalhado,
mostra a taxa contratual separada do aluguel e gera um **CSV com a projeção dos 12 primeiros meses**.

> Repositório: `COLE_AQUI_O_LINK_DO_GITHUB`
> Vídeo pitch: `COLE_AQUI_O_LINK_DO_YOUTUBE`

---

## Regras comerciais implementadas

| Item | Apartamento | Casa | Estúdio |
|---|---|---|---|
| Aluguel-base (1 quarto) | R$ 700,00 | R$ 900,00 | R$ 1.200,00 |
| 2º quarto | + R$ 200,00 | + R$ 250,00 | não se aplica |
| Garagem | 1 vaga: + R$ 300,00 | 1 vaga: + R$ 300,00 | pacote 2 vagas: + R$ 250,00; cada vaga extra: + R$ 60,00 |
| Desconto | 5% se o cliente **não** tem crianças, aplicado **depois** dos adicionais | — | — |

**Taxa contratual:** R$ 2.000,00, parcelável de 1 a 5 vezes, exibida separadamente do aluguel e cobrada
apenas nos meses do parcelamento (mês 1 até mês *n*).

### Interpretações adotadas (pontos que o enunciado não detalha)

1. **Garagem do estúdio:** o cliente pode não contratar garagem. Se contratar, recebe o pacote de 2 vagas
   (R$ 250,00); vagas extras custam R$ 60,00 cada. Não há vaga avulsa: quem quer 1 vaga contrata o pacote.
   Foi definido um limite operacional de 8 vagas adicionais (10 no total) para evitar valores absurdos.
2. **Casa e apartamento:** no máximo 1 vaga de garagem (o enunciado fala em "uma vaga").
3. **Base do desconto:** os 5% incidem sobre aluguel-base + todos os adicionais do apartamento
   (2º quarto e garagem), conforme "após a aplicação dos adicionais correspondentes".
4. **Parcelas não exatas:** 2.000 ÷ 3 não fecha em centavos. O sistema distribui os centavos restantes nas
   primeiras parcelas (666,67 + 666,67 + 666,66), garantindo soma exata de R$ 2.000,00.
5. **Projeção:** o mês 1 é o primeiro mês do contrato; a parcela *k* da taxa é cobrada no mês *k*.

---

## Estrutura do projeto

```
RentSmart/
├── main.py                  # ponto de entrada (python main.py)
├── rentsmart/               # pacote com as classes do sistema
│   ├── __init__.py
│   ├── imoveis.py           # Imovel (abstrata), ImovelResidencial, Apartamento, Casa, Estudio, ItemOrcamento
│   ├── contrato.py          # TaxaContratual (parcelamento da taxa)
│   ├── orcamento.py         # Orcamento e LinhaProjecao (cálculo e projeção de 12 meses)
│   ├── gerador_csv.py       # GeradorCSV (exportação da projeção)
│   ├── interface.py         # InterfaceTerminal (menu, leitura validada, exibição)
│   └── moeda.py             # arredondamento e formatação em R$ com Decimal
├── tests/
│   └── test_regras.py       # 35 testes automatizados (unittest)
├── exemplos/
│   ├── projecao_exemplo_apartamento.csv   # CSV gerado por uma execução real
│   ├── execucao_exemplo.txt               # saída do terminal dessa execução
│   └── resultado_testes.txt               # saída real da execução dos testes
├── docs/
│   ├── Relatorio_RentSmart_VitorBarioniFerraz.pdf   # parte teórica
│   ├── fluxograma/                          # fluxograma em SVG e PNG (partes 1 e 2)
│   └── roteiro_video_pitch.md               # roteiro do vídeo de até 4 minutos
├── CHECKLIST_ENTREGA.md
├── .gitignore
└── README.md
```

O projeto usa **somente a biblioteca padrão do Python** (`decimal`, `csv`, `abc`, `dataclasses`,
`pathlib`, `datetime`, `unittest`), por isso **não há `requirements.txt`**.

---

## Requisitos

- Python **3.10 ou superior** (testado com Python 3.12.10 no Windows 10).
- Nenhuma biblioteca externa.

## Como executar no Windows (terminal do VS Code)

1. Instale o Python em <https://www.python.org/downloads/> marcando **"Add python.exe to PATH"**
   (ou, no terminal: `winget install Python.Python.3.12`).
2. Abra a pasta `RentSmart` no VS Code (**File > Open Folder...**).
3. Abra o terminal integrado: **Terminal > New Terminal** (ou `Ctrl + '`).
4. Confira a instalação:
   ```powershell
   python --version
   ```
5. Execute o sistema:
   ```powershell
   python main.py
   ```
6. Siga o menu. Ao final de cada orçamento, o CSV é salvo na pasta `saida/` com nome
   `projecao_12_meses_AAAAMMDD_HHMMSS.csv`. O caminho completo aparece no terminal.
7. Para abrir o CSV: `start saida\NOME_DO_ARQUIVO.csv` (abre no Excel) ou clique no arquivo no VS Code.

### Exemplo de uso

```
[1] Novo orçamento -> [1] Apartamento -> 2 quartos -> garagem: s -> possui crianças: n -> parcelas: 3
```
Resultado: aluguel mensal **R$ 1.140,00** (700 + 200 + 300 = 1.200; − 5% = 1.140) e taxa em
3x (666,67 + 666,67 + 666,66). A saída completa está em `exemplos/execucao_exemplo.txt`.

## Como rodar os testes

```powershell
python -m unittest discover -s tests -v
```

Os testes cobrem: os três tipos de imóvel com e sem adicionais, desconto de 5% (com e sem crianças,
aplicado depois dos adicionais), regras de garagem do estúdio, parcelamentos de 1 a 5 vezes (inclusive
o caso 2.000 ÷ 3), valores inválidos, projeção de 12 meses, conteúdo do CSV e o fluxo completo do
terminal simulando um usuário que digita respostas inválidas.

---

## Como publicar no GitHub

1. Crie uma conta em <https://github.com> (se ainda não tiver) e instale o Git:
   `winget install Git.Git` (feche e reabra o VS Code depois).
2. Configure seu nome e e-mail (uma única vez):
   ```powershell
   git config --global user.name "Seu Nome"
   git config --global user.email "seu-email@exemplo.com"
   ```
3. No GitHub, clique em **New repository**, nome sugerido `rentsmart`, visibilidade **Public**,
   **sem** marcar README/.gitignore (o projeto já tem). Clique em **Create repository**.
4. No terminal do VS Code, dentro da pasta `RentSmart`:
   ```powershell
   git init
   git add .
   git commit -m "RentSmart: sistema de orçamento de locação com POO"
   git branch -M main
   git remote add origin https://github.com/SEU_USUARIO/rentsmart.git
   git push -u origin main
   ```
   Na primeira vez, o Git abre o navegador para você autorizar o acesso.
5. Abra o link do repositório no navegador e confira se aparecem `main.py`, `rentsmart/`, `tests/`,
   `exemplos/`, `docs/` e o README.
6. Copie o link e cole no topo deste README (campo "Repositório"), depois:
   ```powershell
   git add README.md
   git commit -m "Adiciona links do repositório e do vídeo"
   git push
   ```

Alternativa sem linha de comando: no repositório vazio do GitHub, use **"uploading an existing file"** e
arraste o conteúdo da pasta `RentSmart` (exceto `saida/` e `__pycache__/`).

---

## Fontes consultadas

- Python Software Foundation. *Documentação oficial do Python 3* — <https://docs.python.org/3/>
  (módulos `decimal`, `csv`, `abc`, `dataclasses`, `unittest`).
- Material da disciplina *Algorithmic Thinking & Introduction to Object-Oriented Programming* (AVA UNIFECAF).
