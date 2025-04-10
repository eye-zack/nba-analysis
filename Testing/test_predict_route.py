import unittest
from fastapi.testclient import TestClient
from api_server import app

class TestPredictRoute(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    # test for successful prediction request with valid parameters
    def test_predict_endpoint_success(self):
        # tests the /predict endpoint by sending a valid request with correct queries
        # GET request
        response = self.client.get("/predict", params={
            "team": "GSW",
            "season": 2023,
            "targets": ["3P", "3PA"]
        })

        # remove comment for large DB data dump.
        # print("RESPONSE DATA:", response.json())

        # assertions to check if the result was successful
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        # check that the response is not empty, it contains the predicted data fields
        if response.json():
            self.assertIn("Predicted_3P", response.json()[0])
            self.assertIn("Predicted_3PA", response.json()[0])

    # test for invalid target which should cause a 400 error
    def test_predict_invalid_target(self):
        # GET request
        response = self.client.get("/predict", params={
            "targets": ["InvalidStat"]
        })

        # uncomment for debugging response
        #print("INVALID TARGET RESPONSE:", response.json())

        # assertion to validate a correct 400 response
        self.assertEqual(response.status_code, 400)
        self.assertIn("Unsupported targets", response.json()["detail"])

if __name__ == "__main__":
    unittest.main()


'''The test was failing because of an incorrect assertion on the response keys.
    Originally was using Predicted_3P, Predicted_3PA instead of 3P and 3PA.  
    For future reference, verify correct assertion prior to testing.'''
