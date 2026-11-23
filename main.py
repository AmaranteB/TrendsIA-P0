import os
import re
import sys

import openai
from dotenv import load_dotenv
from openai import OpenAI


MODELO = "gpt-5.4-mini"

CATEGORIAS = {
    "Hardware",
    "Software",
    "Redes",
    "Impressoras",
    "Acesso e contas",
}
PRIORIDADES = {"Baixa", "Média", "Alta"}

INSTRUCOES = """
Você é um classificador de chamados de suporte técnico.

Use somente as informações presentes na descrição. Não presuma, complete ou
invente detalhes. Escolha exatamente uma categoria e uma prioridade das listas.

Responda com exatamente três linhas neste formato:
Categoria: <Hardware, Software, Redes, Impressoras ou Acesso e contas>
Prioridade sugerida: <Baixa, Média ou Alta>
Resumo do problema: <resumo com no máximo 30 palavras>
"""


class ErroConfiguracao(Exception):
    """Indica uma configuração local ausente ou inválida."""


class ErroResposta(Exception):
    """Indica uma resposta vazia ou fora do formato esperado."""


def capturar_entrada():
    """Lê e valida a descrição digitada no terminal."""
    try:
        descricao = input("Descreva o problema de informática: ").strip()
    except EOFError:
        raise ValueError("Nenhuma descrição foi recebida.") from None

    if not descricao:
        raise ValueError("A descrição não pode ficar vazia.")

    return descricao


def carregar_configuracao():
    """Carrega e valida a chave da API sem exibi-la."""
    load_dotenv()
    chave = os.getenv("OPENAI_API_KEY", "").strip()

    valores_de_exemplo = {
        "coloque_sua_chave_aqui",
        "sua_chave_real_aqui",
        "your_api_key_here",
    }
    if not chave or chave in valores_de_exemplo:
        raise ErroConfiguracao(
            "A chave da API não foi configurada. Preencha OPENAI_API_KEY no arquivo .env."
        )

    if "\n" in chave or "\r" in chave:
        raise ErroConfiguracao("A configuração da chave da API está inválida.")

    if not MODELO.strip():
        raise ErroConfiguracao("O modelo da API não foi configurado no programa.")

    return chave


def preparar_solicitacao(descricao):
    """Monta os parâmetros da chamada ao modelo."""
    return {
        "model": MODELO,
        "instructions": INSTRUCOES,
        "input": descricao,
    }


def chamar_modelo(cliente, solicitacao):
    """Envia a solicitação ao modelo usando o cliente recebido."""
    return cliente.responses.create(**solicitacao)


def tratar_resposta(resposta):
    """Confere se o texto retornado segue os campos e limites definidos."""
    texto = getattr(resposta, "output_text", None)
    if not isinstance(texto, str) or not texto.strip():
        raise ErroResposta("O serviço retornou uma resposta vazia.")

    linhas = [linha.strip() for linha in texto.splitlines() if linha.strip()]
    if len(linhas) != 3:
        raise ErroResposta("O serviço retornou uma resposta em formato inesperado.")

    campos_esperados = (
        "Categoria:",
        "Prioridade sugerida:",
        "Resumo do problema:",
    )
    if any(not linha.startswith(campo) for linha, campo in zip(linhas, campos_esperados)):
        raise ErroResposta("O serviço retornou uma resposta em formato inesperado.")

    categoria = linhas[0].split(":", 1)[1].strip()
    prioridade = linhas[1].split(":", 1)[1].strip()
    resumo = linhas[2].split(":", 1)[1].strip()

    if categoria not in CATEGORIAS or prioridade not in PRIORIDADES or not resumo:
        raise ErroResposta("O serviço retornou uma resposta em formato inesperado.")

    if len(re.findall(r"\b\w+\b", resumo, flags=re.UNICODE)) > 30:
        raise ErroResposta("O serviço retornou um resumo com mais de 30 palavras.")

    return "\n".join(linhas)


def apresentar_resultado(resultado):
    """Mostra a classificação validada no terminal."""
    print("\nClassificação do chamado:")
    print(resultado)


def mensagem_de_erro(erro):
    """Converte erros previsíveis em mensagens para quem usa o programa."""
    if isinstance(erro, ErroConfiguracao):
        return str(erro)
    if isinstance(erro, openai.AuthenticationError):
        return "A chave da API foi recusada. Confira se está correta e ativa."
    if isinstance(erro, openai.APITimeoutError):
        return "A solicitação demorou demais e excedeu o tempo limite. Tente novamente."
    if isinstance(erro, openai.APIConnectionError):
        return "Não foi possível conectar à API. Confira sua internet e tente novamente."
    if isinstance(erro, openai.NotFoundError):
        return "O modelo configurado não foi encontrado ou não está disponível para esta conta."
    if isinstance(erro, openai.PermissionDeniedError):
        return "A conta não tem acesso ao modelo ou recurso solicitado. Confira as permissões da API."
    if isinstance(erro, openai.RateLimitError):
        codigo = getattr(erro, "code", None)
        if codigo in {"insufficient_quota", "credit_balance_exhausted"}:
            return "A conta da API está sem créditos ou atingiu seu limite de uso. Confira o faturamento."
        return "A API recebeu solicitações demais. Aguarde um pouco e tente novamente."
    if isinstance(erro, openai.APIStatusError):
        return "A API não conseguiu processar a solicitação. Tente novamente mais tarde."
    if isinstance(erro, ErroResposta):
        return str(erro)
    if isinstance(erro, ValueError):
        return str(erro)
    return "Ocorreu um erro inesperado. Confira a configuração e tente novamente."


def main():
    """Coordena a execução da aplicação e encerra com uma mensagem clara."""
    try:
        descricao = capturar_entrada()
        chave = carregar_configuracao()
        cliente = OpenAI(api_key=chave)
        solicitacao = preparar_solicitacao(descricao)
        resposta = chamar_modelo(cliente, solicitacao)
        resultado = tratar_resposta(resposta)
        apresentar_resultado(resultado)
        return 0
    except KeyboardInterrupt:
        mensagem = "Operação cancelada pelo usuário."
    except (ValueError, ErroConfiguracao, ErroResposta) as erro:
        mensagem = mensagem_de_erro(erro)
    except openai.AuthenticationError as erro:
        mensagem = mensagem_de_erro(erro)
    except openai.APITimeoutError as erro:
        mensagem = mensagem_de_erro(erro)
    except openai.APIConnectionError as erro:
        mensagem = mensagem_de_erro(erro)
    except openai.NotFoundError as erro:
        mensagem = mensagem_de_erro(erro)
    except openai.PermissionDeniedError as erro:
        mensagem = mensagem_de_erro(erro)
    except openai.RateLimitError as erro:
        mensagem = mensagem_de_erro(erro)
    except openai.APIStatusError as erro:
        mensagem = mensagem_de_erro(erro)
    except Exception as erro:
        mensagem = mensagem_de_erro(erro)

    print(f"Erro: {mensagem}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
