# Classificador Inteligente de Chamados de Suporte Técnico

Versão intermediária de um projeto acadêmico em Python. A aplicação recebe
uma descrição pelo terminal e usa a API da OpenAI para sugerir uma categoria,
uma prioridade e um resumo curto.

## O que a aplicação retorna

- Categoria: Hardware, Software, Redes, Impressoras ou Acesso e contas;
- Prioridade sugerida: Baixa, Média ou Alta;
- Resumo do problema: até 30 palavras.

O modelo recebe a instrução de usar somente o conteúdo informado pelo usuário.
A aplicação confere se a resposta não está vazia e se contém os campos,
valores e limite de palavras esperados.

## Arquivos

```text
.
|-- main.py
|-- test_main.py
|-- requirements.txt
|-- .env.example
|-- .gitignore
`-- README.md
```

## Requisitos

- Python 3.10 ou superior;
- uma chave da API da OpenAI com acesso ao modelo configurado;
- créditos ou faturamento habilitado na organização da API para executar uma
  chamada real.

A assinatura do ChatGPT Plus não paga chamadas feitas pela API. O uso da API é
faturado separadamente e depende da conta, modelo e tokens utilizados.

## Instalação no Windows

Abra o terminal do VS Code na pasta do projeto e crie um ambiente virtual:

```powershell
python -m venv .venv
```

Ative-o no PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

No Prompt de Comando (cmd), use:

```cmd
.venv\Scripts\activate.bat
```

Instale as dependências:

```powershell
python -m pip install -r requirements.txt
```

## Configuração da API

1. Crie uma chave em <https://platform.openai.com/api-keys>.
2. Copie o arquivo de exemplo para criar o arquivo local `.env`:

   ```powershell
   Copy-Item .env.example .env
   ```

3. Edite `.env` e substitua o valor de exemplo pela sua chave:

   ```env
   OPENAI_API_KEY=sua_chave_real_aqui
   ```

O programa carrega essa variável com `python-dotenv`. A chave não é mostrada
nas mensagens de erro. O `.gitignore` exclui `.env` e suas variantes, mas
permite versionar `.env.example`. Nunca publique uma chave real.

O modelo está definido pela constante `MODELO` no início de `main.py` e pode
ser trocado por outro modelo de texto acessível à organização da API. Esta
versão mantém essa escolha no código; configuração externa é uma evolução do
nível avançado.

## Execução real

Com o ambiente virtual ativo e a chave configurada:

```powershell
python main.py
```

Exemplo de entrada:

```text
Descreva o problema de informática: Não consigo acessar o e-mail porque minha senha foi bloqueada.
```

Exemplo de saída possível:

```text
Classificação do chamado:
Categoria: Acesso e contas
Prioridade sugerida: Média
Resumo do problema: Usuário não consegue acessar o e-mail porque a senha está bloqueada.
```

A saída pode variar. Uma execução real envia a descrição à API e pode consumir
créditos. Se a conta estiver sem saldo, o programa explica que é necessário
conferir o faturamento.

## Testes simulados

Execute os testes automatizados com:

```powershell
python -m unittest -v
```

Os testes usam `unittest.mock` para simular respostas e erros. Eles cobrem
entrada vazia, configuração sem credencial, credencial inválida, timeout,
falha de conexão, modelo não encontrado, saldo esgotado e respostas vazias ou
fora do formato. **Não fazem chamadas reais à API, não precisam de uma chave
válida e não consomem créditos.**

Para demonstrar uma credencial ausente ou inválida com os testes simulados,
rode o comando acima. Para testar o fluxo real do serviço, configure uma chave
válida e saldo disponível e rode `python main.py`. Os dois tipos de execução
validam coisas diferentes.

## Como o código está organizado

- `capturar_entrada()` lê e rejeita descrições vazias;
- `carregar_configuracao()` carrega e verifica se a chave local foi informada;
- `preparar_solicitacao()` monta os parâmetros enviados ao modelo;
- `chamar_modelo()` faz a chamada pelo SDK oficial;
- `tratar_resposta()` rejeita saída vazia, campos ou valores inválidos e resumo
  acima de 30 palavras;
- `apresentar_resultado()` imprime a classificação;
- `mensagem_de_erro()` converte falhas previsíveis em mensagens compreensíveis.

Erros de autenticação, timeout, conexão, modelo ou permissões e respostas da
API são tratados separadamente. Quando a conta não tem créditos, o programa
orienta conferir faturamento. A indisponibilidade do serviço ou a recuperação
da infraestrutura depende do provedor ou da equipe que a administra.

## Dependências

- `openai`: SDK oficial da API da OpenAI;
- `python-dotenv`: carrega `OPENAI_API_KEY` do arquivo `.env`.

## Referências oficiais

- [SDKs da OpenAI](https://developers.openai.com/api/docs/libraries)
- [Erros da API](https://developers.openai.com/api/docs/guides/error-codes)
- [Modelos disponíveis](https://developers.openai.com/api/docs/models)
- [Chaves da API](https://platform.openai.com/api-keys)
