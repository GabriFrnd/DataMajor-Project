# 📊 Data Major — Tópicos de Banco de Dados

Projeto acadêmico desenvolvido para a disciplina **Tópicos de Banco de Dados** do curso de Ciência da Computação do Centro Universitário IESB, semestre de 2026.

---

## 📝 Descrição do Projeto

O projeto tem como objetivo consolidar, de forma prática e técnica, os conteúdos estudados ao longo da disciplina, demonstrando domínio do ciclo completo de dados:

**Coleta → Tratamento → Armazenamento → Modelagem → Análise → Interpretação**

---

## 📦 Dataset

- **Fonte:** [Facebook Reviews — Play Store (Kaggle)](https://www.kaggle.com/datasets/ashishkumarak/play-store-reviews-facebook)
- **Formato:** CSV
- **Descrição:** Reviews do aplicativo Facebook disponíveis na Google Play Store, contendo avaliações, notas e outros metadados dos usuários.

---

## 🛠️ Tecnologias Utilizadas

- Python 3.x
- kagglehub
- pandas
- MongoDB ou Parquet *(a definir)*

---

## 📁 Estrutura de Pastas

```
/
├── data/
│   ├── raw/          # Dados brutos, gerados pelo script de Extract
│   └── processed/    # Dados tratados, gerados pelo Transform
├── notebooks/
│   ├── extract/      # Notebooks da etapa de Extract
│   ├── transform/    # Notebooks da etapa de Transform
│   ├── load/         # Notebooks da etapa de Load
│   └── mining/       # Notebooks da etapa de Mineração
├── pipeline/
│   ├── extract/      # Scripts de coleta e download do dataset
│   ├── transform/    # Scripts de limpeza e padronização
│   ├── load/         # Scripts de armazenamento
│   └── mining/       # Scripts de mineração e análise
├── docs/             # Decisões arquiteturais e justificativas
├── README.md
└── requirements.txt
```

> ⚠️ A pasta `data/` não é versionada no repositório. Ela é gerada localmente ao executar o script de Extract.

---

## ⚙️ Como Executar

### 1. Clone o repositório

```bash
git clone https://github.com/[usuario]/[repositorio].git
cd [repositorio]
```

### 2. Crie e ative o ambiente virtual

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Execute o script de Extract

```bash
python pipeline/extract/system.py
```

> O script realizará automaticamente o download do dataset e o organizará em `data/raw/`.

### 5. Carregando o DataFrame

Para carregar o DataFrame do projeto, importe e chame a função `load_dataframe()` do arquivo `pipeline/extract/main.py`:

```python
from main import load_dataframe

df = load_dataframe()
```

> A função `load_dataframe()` é autossuficiente — ela realiza o download do dataset, detecta o encoding e o delimitador automaticamente, e retorna o DataFrame pronto para uso.

### 6. Executando a etapa de Load com MongoDB

Depois de rodar o Transform, execute a carga para o MongoDB:

```bash
python pipeline/load/main.py
```

Por padrão, o script usa `mongodb://localhost:27017`. Se necessário, defina a variável de ambiente `MONGODB_URI` antes de executar.

> A collection padrão é `data_major.facebook_reviews`, com índices em `reviewId`, `at` e `sentiment` para suportar consultas e análise posterior.

**Notebook — Load Validation**

O notebook `notebooks/load/explorer.ipynb` contém as células de verificação automatizadas para a etapa de Load:

- Objetivo: validar a carga no MongoDB, conferir contagem de documentos, mostrar amostras e executar consultas de exemplo.
- Consulta de exemplo: busca por `sentiment = 'positivo'` e exibição de 5 registros.

Justificativa Arquitetural (migrada do notebook):

> A etapa de Load usa MongoDB porque o dataset é textual, a estrutura pode evoluir e a consulta analítica se beneficia de documentos flexíveis. Os índices em `reviewId`, `at` e `sentiment` aceleram buscas por identificação, análise temporal e filtros por polaridade.

---

## 📓 Jupyter Notebook

### Instalação da extensão 

Para utilizar os notebooks do projeto no VS Code, instale a extensão **Jupyter** disponível na aba de extensões (`Ctrl+Shift+X`).

Além disso, instale o `ipykernel` no ambiente virtual:

```bash
pip install ipykernel
```

### Seleção do interpretador

Ao abrir um notebook `.ipynb`, selecione o interpretador correto no canto superior direito do VS Code. Escolha o Python do ambiente virtual `venv` do projeto.

> ⚠️ Utilizar um interpretador diferente do ambiente virtual fará com que as bibliotecas do projeto não sejam encontradas.

### Atualização do requirements.txt

Sempre que instalar uma nova biblioteca, atualize o `requirements.txt` com o comando:

```bash
pip freeze > requirements.txt
```

> Lembre-se de commitar o `requirements.txt` atualizado para que os outros integrantes possam instalar as novas dependências.

---

## 📋 Padrão de Commits

Este projeto segue a convenção [Conventional Commits](https://www.conventionalcommits.org/):

```
<tipo>(escopo): descrição curta
```

**Tipos utilizados:**

- `feat` — nova funcionalidade
- `fix` — correção de bug
- `docs` — alterações em documentação
- `refactor` — refatoração sem mudança de comportamento
- `chore` — tarefas auxiliares (configuração, dependências)
- `style` — formatação, sem impacto lógico

**Exemplos:**

```
feat(extract): add automated download script for kaggle dataset
docs(readme): add project structure and contribution guidelines
chore: add .gitignore for python and venv
```