import unittest
from unittest.mock import patch, MagicMock
from requests.exceptions import HTTPError

# Importa a classe do seu projeto
from utils.wfs_geosampa.get_features import GeoSampaWFSFetcher

class TestGeoSampaWFSFetcher(unittest.TestCase):

    def setUp(self):
        # Iniciamos com verbose False para não poluir o output dos testes
        self.fetcher = GeoSampaWFSFetcher(start_index=0, verbose=False)
        self.nome_camada = "lote_cidadao"

    def test_init_parameters(self):
        """Verifica se os atributos de instância são iniciados corretamente."""
        fetcher = GeoSampaWFSFetcher(start_index=100, verbose=True)
        self.assertEqual(fetcher.start_index, 100)
        self.assertTrue(fetcher.verbose)
        self.assertEqual(fetcher.features_fetched_count, 0)

    def test_gen_parameters_max_features(self):
        """Valida se o parâmetro count é mapeado para maxFeatures."""
        params = self.fetcher.gen_get_features_parameters(
            self.nome_camada, 
            count=50, 
            start_index=10
        )
        self.assertEqual(params["maxFeatures"], 50)
        self.assertEqual(params["startIndex"], 10)
        self.assertEqual(params["typeName"], "geoportal:lote_cidadao")

    @patch('requests.get')
    def test_get_layer_data_metadata_and_features(self, mock_get):
        """Verifica se o json é retornado corretamente e se levanta erro no status != 200."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_data = {
            "features": [{"id": 1}],
            "numberMatched": 100,
            "numberReturned": 1
        }
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        res = self.fetcher.get_layer_data(self.nome_camada)
        self.assertEqual(res["numberMatched"], 100)
        mock_get.assert_called_once()

    @patch('requests.get')
    def test_fetch_feature_batches_logic(self, mock_get):
        """
        Testa a lógica do loop:
        1. Atualização do features_fetched_count.
        2. Atualização do last_resp_metadata (sem a chave features).
        3. Incremento do start_index baseado na quantidade real retornada.
        """
        # Simula resposta de um batch
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Simulando que temos 10 no total, mas retornamos 5 agora
        mock_response.json.return_value = {
            "features": [{"id": i} for i in range(5)],
            "numberMatched": 10,
            "totalFeatures": 10
        }
        mock_get.return_value = mock_response

        # Pegamos apenas o primeiro batch do generator
        gen = self.fetcher.fetch_feature_batches(self.nome_camada, count=5)
        batch = next(gen)

        self.assertEqual(len(batch), 5)
        self.assertEqual(self.fetcher.features_fetched_count, 5)
        self.assertEqual(self.fetcher.start_index, 5)
        # Verifica se o metadata foi guardado e a chave 'features' removida dele
        self.assertIn("numberMatched", self.fetcher.last_resp_metadata)
        self.assertNotIn("features", self.fetcher.last_resp_metadata)

    @patch('requests.get')
    def test_iteration_stop_condition(self, mock_get):
        """Garante que o loop para quando o total de features buscadas atinge o matched."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Retorna 2 features e diz que só existem 2 no total
        mock_response.json.return_value = {
            "features": [{"id": 1}, {"id": 2}],
            "numberMatched": 2
        }
        mock_get.return_value = mock_response

        # Converte o generator em lista (deve rodar apenas uma vez)
        all_batches = list(self.fetcher(self.nome_camada))
        
        self.assertEqual(len(all_batches), 1)
        self.assertEqual(mock_get.call_count, 1)

    @patch('requests.get')
    def test_http_error_handling(self, mock_get):
        """Valida o raise_for_status."""
        mock_response = MagicMock()
        mock_response.status_code = 504 # Gateway Timeout comum no Geosampa
        mock_response.raise_for_status.side_effect = HTTPError("Timeout")
        mock_get.return_value = mock_response

        with self.assertRaises(HTTPError):
            self.fetcher.get_layer_data(self.nome_camada)

if __name__ == '__main__':
    unittest.main()