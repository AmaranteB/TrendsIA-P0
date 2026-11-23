from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

MODELO = "gpt-5.4-mini"

INSTRUCOES = """
Você é um classificador de chamados de suporte técnico.

Analise somente a descrição enviada pelo usuário. Não presuma, complete ou
invente informações que não estejam no texto.

Responda exatamente neste formato:
Categoria: <Hardware, Software, Redes, Impressoras ou Acesso e contas>
Prioridade sugerida: <Baixa, Média ou Alta>
Resumo do problema: <resumo com no máximo 30 palavras>

Escolha somente uma categoria e uma prioridade entre as opções permitidas.
"""

descricao = input("Descreva o problema de informática: ")

cliente = OpenAI()

resposta = cliente.responses.create(
    model=MODELO,
    instructions=INSTRUCOES,
    input=descricao,
)

print("\nClassificação do chamado:")
print(resposta.output_text)
