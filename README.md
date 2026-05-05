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
python pipeline/extract/main.py
```

> O script realizará automaticamente o download do dataset e o organizará em `data/raw/`.

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

---

## 🌿 Padrão de Branches

```
<tipo>/<descrição>
```

**Tipos utilizados:**

- `feature/` — desenvolvimento de uma etapa do pipeline
- `fix/` — correção de problemas
- `docs/` — alterações em documentação

**Exemplos:**

```
feature/extract
feature/transform
feature/load
feature/mining
```