import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import openai

import main


def criar_erro_api(tipo_erro, status):
    request = Mock()
    request.url = "https://api.openai.com/v1/responses"
    response = Mock()
    response.status_code = status
    response.request = request
    response.headers = {}
    return tipo_erro(
        "erro simulado para teste",
        response=response,
        body={"error": {"message": "erro simulado"}},
    )


class TestEntradaEConfiguracao(unittest.TestCase):
    def test_impede_descricao_vazia(self):
        with patch("builtins.input", return_value="   "):
            with self.assertRaisesRegex(ValueError, "não pode ficar vazia"):
                main.capturar_entrada()

    def test_credencial_ausente_e_rejeitada_sem_chamar_api(self):
        with patch.dict(os.environ, {}, clear=True), patch("main.load_dotenv"):
            with self.assertRaisesRegex(main.ErroConfiguracao, "OPENAI_API_KEY"):
                main.carregar_configuracao()

    def test_valor_de_exemplo_nao_e_aceito_como_credencial(self):
        with patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "coloque_sua_chave_aqui"},
            clear=True,
        ), patch("main.load_dotenv"):
            with self.assertRaises(main.ErroConfiguracao):
                main.carregar_configuracao()


class TestTratamentoDeResposta(unittest.TestCase):
    def test_aceita_resposta_com_formato_valido(self):
        resposta = SimpleNamespace(
            output_text=(
                "Categoria: Redes\n"
                "Prioridade sugerida: Média\n"
                "Resumo do problema: Conexão Wi-Fi cai com frequência."
            )
        )
        self.assertIn("Categoria: Redes", main.tratar_resposta(resposta))

    def test_rejeita_resposta_vazia(self):
        with self.assertRaisesRegex(main.ErroResposta, "vazia"):
            main.tratar_resposta(SimpleNamespace(output_text="  "))

    def test_rejeita_formato_inesperado(self):
        resposta = SimpleNamespace(output_text="Parece ser um problema de rede.")
        with self.assertRaisesRegex(main.ErroResposta, "formato inesperado"):
            main.tratar_resposta(resposta)

    def test_rejeita_categoria_fora_da_lista(self):
        resposta = SimpleNamespace(
            output_text=(
                "Categoria: Telefonia\n"
                "Prioridade sugerida: Média\n"
                "Resumo do problema: Falha relatada pelo usuário."
            )
        )
        with self.assertRaises(main.ErroResposta):
            main.tratar_resposta(resposta)

    def test_rejeita_resumo_com_mais_de_30_palavras(self):
        resumo = " ".join(["palavra"] * 31)
        resposta = SimpleNamespace(
            output_text=(
                "Categoria: Software\n"
                "Prioridade sugerida: Baixa\n"
                f"Resumo do problema: {resumo}"
            )
        )
        with self.assertRaisesRegex(main.ErroResposta, "mais de 30 palavras"):
            main.tratar_resposta(resposta)


class TestErrosDeIntegracaoSimulada(unittest.TestCase):
    def test_credencial_ausente_encerra_sem_tentar_criar_cliente(self):
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("main.load_dotenv"),
            patch("builtins.input", return_value="Meu computador não liga."),
            patch("main.OpenAI") as cliente,
            patch("sys.stderr") as stderr,
        ):
            codigo_saida = main.main()

        self.assertEqual(codigo_saida, 1)
        mensagem = "".join(chamada.args[0] for chamada in stderr.write.call_args_list)
        self.assertIn("não foi configurada", mensagem)
        self.assertNotIn("Traceback", mensagem)
        cliente.assert_not_called()

    def test_credencial_invalida_mostra_mensagem_segura(self):
        erro = criar_erro_api(openai.AuthenticationError, 401)
        cliente = Mock()
        cliente.responses.create.side_effect = erro

        with (
            patch.dict(os.environ, {"OPENAI_API_KEY": "credencial-ficticia"}, clear=True),
            patch("main.load_dotenv"),
            patch("builtins.input", return_value="Meu computador não liga."),
            patch("main.OpenAI", return_value=cliente),
            patch("sys.stderr") as stderr,
        ):
            codigo_saida = main.main()

        self.assertEqual(codigo_saida, 1)
        mensagem = "".join(chamada.args[0] for chamada in stderr.write.call_args_list)
        self.assertIn("chave da API foi recusada", mensagem)
        self.assertNotIn("credencial-ficticia", mensagem)
        self.assertNotIn("Traceback", mensagem)
        cliente.responses.create.assert_called_once()

    def test_timeout_tem_mensagem_compreensivel(self):
        erro = openai.APITimeoutError(request=Mock())
        self.assertIn("tempo limite", main.mensagem_de_erro(erro))

    def test_falha_de_conexao_tem_mensagem_compreensivel(self):
        erro = openai.APIConnectionError(
            message="falha simulada",
            request=Mock(),
        )
        self.assertIn("conectar à API", main.mensagem_de_erro(erro))

    def test_modelo_indisponivel_tem_mensagem_compreensivel(self):
        erro = criar_erro_api(openai.NotFoundError, 404)
        self.assertIn("modelo configurado", main.mensagem_de_erro(erro))

    def test_creditos_esgotados_sao_explicados(self):
        erro = criar_erro_api(openai.RateLimitError, 429)
        erro.code = "insufficient_quota"
        self.assertIn("sem créditos", main.mensagem_de_erro(erro))


if __name__ == "__main__":
    unittest.main()
