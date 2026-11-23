# Classificador Inteligente de Chamados de Suporte Técnico

Versão básica de uma aplicação acadêmica em Python que recebe, pelo terminal,
a descrição de um problema de informática e usa a API da OpenAI para sugerir:

- uma categoria: Hardware, Software, Redes, Impressoras ou Acesso e contas;
- uma prioridade: Baixa, Média ou Alta;
- um resumo do problema com até 30 palavras.

O modelo é instruído a usar apenas as informações fornecidas pelo usuário e a
não inventar detalhes.

## Estrutura do projeto

```text
.
|-- main.py
|-- requirements.txt
|-- .env.example
|-- .gitignore
`-- README.md
```

## Pré-requisitos

- Python instalado no Windows;
- uma chave da API da OpenAI;
- créditos ou faturamento habilitado na conta da API, quando necessário.

O uso da API é separado de uma assinatura do ChatGPT e pode gerar cobrança de
acordo com o modelo e a quantidade de tokens utilizados.

## Instalação no Windows

Abra o terminal do VS Code na pasta do projeto e crie um ambiente virtual:

```powershell
python -m venv .venv
```

Ative o ambiente virtual no PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Se estiver usando o Prompt de Comando (cmd), utilize:

```cmd
.venv\Scripts\activate.bat
```

Instale as dependências:

```powershell
python -m pip install -r requirements.txt
```

## Configuração da chave da API

1. Crie sua própria chave em <https://platform.openai.com/api-keys>.
2. Copie o arquivo de exemplo para um novo arquivo chamado `.env`:

```powershell
Copy-Item .env.example .env
```

3. Abra o `.env` e substitua o valor de exemplo pela sua chave real:

```env
OPENAI_API_KEY=sua_chave_real_aqui
```

O arquivo `.env` está listado no `.gitignore` e não deve ser enviado ao GitHub.
O arquivo `.env.example` contém apenas um valor fictício e pode ser versionado.

## Modelo utilizado

O modelo está definido na constante `MODELO`, no início do `main.py`:

```python
MODELO = "gpt-5.4-mini"
```

Esse modelo aceita texto pela Responses API e é adequado para a classificação
solicitada. A disponibilidade depende da conta da API. Se a conta não tiver
acesso a ele, altere somente o valor da constante para outro modelo de texto
disponível na sua conta. Consulte a lista atual em
<https://developers.openai.com/api/docs/models>.

## Execução

Com o ambiente virtual ativado e o `.env` configurado, execute:

```powershell
python main.py
```

Digite a descrição quando o programa solicitar. Exemplo:

```text
Descreva o problema de informática: Não consigo entrar no e-mail porque minha senha foi bloqueada.

Classificação do chamado:
Categoria: Acesso e contas
Prioridade sugerida: Média
Resumo do problema: Usuário não consegue acessar o e-mail porque a senha está bloqueada.
```

A classificação pode variar, pois é produzida por um modelo de linguagem.

## Como o código funciona

1. `load_dotenv()` carrega as variáveis do arquivo `.env` para o ambiente do
   programa.
2. `OpenAI()` cria o cliente oficial. O SDK lê automaticamente a variável
   `OPENAI_API_KEY`.
3. `input()` recebe a descrição digitada no terminal.
4. `cliente.responses.create(...)` envia as instruções e a descrição ao modelo.
5. `resposta.output_text` contém o texto retornado e é exibido no terminal.

As instruções separam claramente as opções permitidas, o formato esperado e a
regra de não inventar informações. Nesta versão básica, o retorno é texto
simples: validações, tratamento específico de erros, logs, configuração externa
do modelo e testes serão evoluções posteriores do projeto.

## Dependências

- `openai`: SDK oficial para acessar a API da OpenAI;
- `python-dotenv`: carrega a chave armazenada localmente no arquivo `.env`.

## Segurança

- nunca escreva a chave diretamente no `main.py`;
- nunca publique o arquivo `.env`;
- antes de qualquer commit, confira os arquivos com `git status`;
- se uma chave for exposta, revogue-a no painel da OpenAI e crie outra.

## Referências oficiais

- SDKs da OpenAI: <https://developers.openai.com/api/docs/libraries>
- Modelos disponíveis: <https://developers.openai.com/api/docs/models>
- Chaves da API: <https://platform.openai.com/api-keys>
