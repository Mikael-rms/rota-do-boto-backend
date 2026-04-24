# 🚤 Rota do Boto - Backend

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688)
![Firebase](https://img.shields.io/badge/Firebase-Firestore-orange)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Prototype-yellow)
![Contributions](https://img.shields.io/badge/Contributions-Welcome-brightgreen)

Este é o backend do projeto **Rota do Boto**, desenvolvido com FastAPI e integrado ao Firebase (Firestore).

---

# 📦 Tecnologias utilizadas

* Python
* FastAPI
* Firebase Admin SDK
* Firestore

---

# ⚙️ Configuração do ambiente (PASSO A PASSO)

Siga todos os passos abaixo com atenção.

---

## 1. Clonar o repositório

```bash
git clone https://github.com/Mikael-rms/rota-do-boto-backend.git
cd rota-do-boto-backend/backend
```

---

## 2. Instalar dependências

```bash
pip install fastapi uvicorn firebase-admin python-dotenv
```

---

## 3. Configurar variáveis de ambiente (.env)

### 🔹 3.1 Criar o arquivo

Na pasta `backend`, crie um arquivo chamado:

```
.env
```

---

### 🔹 3.2 Adicionar conteúdo

Dentro do `.env`, coloque:

```env
FIREBASE_CREDENTIALS=./src/config/serviceAccountKey.json
```

---

## 4. Configurar credenciais do Firebase

### ⚠️ IMPORTANTE

Esse arquivo NÃO está no repositório por segurança.

Você deve receber o arquivo `serviceAccountKey.json`.

---

### 🔹 4.1 Onde colocar o arquivo

Coloque o arquivo exatamente neste caminho:

```
src/config/serviceAccountKey.json
```

---

### 🔹 4.2 Estrutura esperada

```
backend/
  src/
    config/
      firebase.py
      serviceAccountKey.json  ← (arquivo local, NÃO vai pro Git)
    main.py
  .env
```

---

## 5. Rodar o projeto

```bash
uvicorn main:app --reload
```

A API estará disponível em:

```
http://127.0.0.1:8000
```

---

# 🔐 Segurança (MUITO IMPORTANTE)

## ❌ NUNCA FAÇA

Não subir para o Git:

* `.env`
* `serviceAccountKey.json`
* qualquer chave/API/token

---

## ✅ Como evitar problemas

Sempre antes de commit:

```bash
git status
```

Se aparecer algo como:

```
.env
src/config/serviceAccountKey.json
```

👉 NÃO FAÇA COMMIT

---

# 🚨 ERRO COMUM (E COMO RESOLVER)

## ❌ Problema: "Push bloqueado por segredo"

Se você ver um erro como:

```
Push cannot contain secrets
Google Cloud Service Account Credentials
```

👉 Isso significa que o arquivo `serviceAccountKey.json` foi commitado.

---

## 🧠 Por que isso acontece?

* O GitHub detecta automaticamente chaves sensíveis
* Mesmo que você delete depois, o histórico ainda contém o segredo
* Por isso o push é bloqueado

---

## ✅ SOLUÇÃO (recomendada para este projeto)

### 🧨 1. Apagar o histórico do Git

Na raiz do projeto:

```bash
Remove-Item -Recurse -Force .git
```

---

### 🔄 2. Recriar o repositório

```bash
git init
git add .
```

---

### ⚠️ 3. Conferir antes do commit

```bash
git status
```

👉 NÃO pode aparecer:

```
.env
src/config/serviceAccountKey.json
```

---

### ✅ 4. Commit limpo

```bash
git commit -m "init: projeto limpo sem credenciais"
```

---

### 🔗 5. Conectar ao GitHub

```bash
git branch -M main
git remote add origin https://github.com/Mikael-rms/rota-do-boto-backend.git
```

---

### 🚀 6. Push forçado

```bash
git push -f origin main
```

---

# 👥 Como funciona em equipe

Cada desenvolvedor precisa:

1. Criar seu próprio `.env`
2. Ter sua cópia do `serviceAccountKey.json`

Esses arquivos NÃO são compartilhados pelo Git.

---

# 📄 .env.example

Este projeto possui um arquivo `.env.example`.

Ele serve como modelo.

### Como usar:

1. Copie o arquivo:

```bash
cp .env.example .env
```

(ou copie manualmente no Windows)

2. Ajuste se necessário

---

# 🧠 Explicação simples do sistema

* O `.env` guarda configurações locais
* O código lê essas configurações automaticamente
* O Firebase usa o caminho do `.env` para acessar a chave

---

# 🚀 Fluxo normal de trabalho

Depois de tudo configurado:

```bash
git add .
git commit -m "feat: qualquer coisa"
git push
```

---

# 🛠 Possíveis erros e soluções

## ❌ Erro: FIREBASE_CREDENTIALS None

Causa:

* `.env` não carregado ou não existe

Solução:

* Verifique se criou o `.env`
* Verifique se escreveu corretamente

---

## ❌ Erro: arquivo não encontrado

Causa:

* caminho errado

Solução:

* confirme se o arquivo está em:

```
src/config/serviceAccountKey.json
```

---

## ❌ Erro ao iniciar servidor

Causa comum:

* dependências não instaladas

Solução:

```bash
pip install fastapi uvicorn firebase-admin python-dotenv
```

---

# 📌 Observações finais

* Este projeto é um protótipo
* Mesmo assim, seguimos boas práticas
* Isso facilita evolução futura

---

# 💡 Dica

Se algo não funcionar:

* Leia este README novamente com calma
* Verifique caminhos e arquivos
* Este README será atualizado conforme o desenvolvimento do projeto

👉 90% dos erros são configuração incorreta

---
