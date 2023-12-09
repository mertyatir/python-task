from flask import Flask, request, jsonify
import pandas as pd
import requests
from io import StringIO

app = Flask(__name__)

@app.route('/api', methods=['POST'])
def api():
    # Convert CSV data to DataFrame
    csv_data = pd.read_csv(StringIO(request.data.decode('utf-8')))


    # Authenticate
    url = "https://api.baubuddy.de/index.php/login"
    payload = {
        "username": "365",
        "password": "1"
    }
    headers = {
        "Authorization": "Basic QVBJX0V4cGxvcmVyOjEyMzQ1NmlzQUxhbWVQYXNz",
        "Content-Type": "application/json"
    }
    response = requests.request("POST", url, json=payload, headers=headers)
    access_token = response.json()["oauth"]["access_token"]

    # Update headers with access token
    headers["Authorization"] = f"Bearer {access_token}"

    # Request resources
    response = requests.get('https://api.baubuddy.de/dev/index.php/v1/vehicles/select/active', headers=headers)

    """
    Response format:
    [
    {
        "rnr": "10",
        "gruppe": "Fahrzeuge",
        "kurzname": "PB V 1300 (Container)",
        "langtext": "MAN 26.440 Kennzeichen PB V 1300.",
        "info": "Dieses Fahrzeug wurde für den Gerüstbau angeschafft.\nEs kann mit der alten Führerscheinklasse 2, bzw mit dem Führerschein Klasse C gefahren werden.\nDie Zuladung beträgt ca. 15.000 KG einschl. Container.\n\n\n!8.9.2023\nZu prüfen in regelmäßigen Abständen\n- Licht und Elektronik, \n- Auspuff, \n- Reifen, \n- Karosserie, \n- Innenraum, \n- Fahrwerk, Lenkung, Bremsen\n- Motorraum//.Öl und andere Flüssigkeiten",
        "sort": "0",
        "lagerort": "Paderborn",
        "lteartikel": "Fahrzeug",
        "businessUnit": "Gerüstbau",
        "vondat": "2007-07-02",
        "bisdat": null,
        "hu": "2023-05-31",
        "asu": "2021-12-01",
        "createdOn": null,
        "editedOn": "2023-10-25T09:37:48Z",
        "fuelConsumption": "25.0",
        "priceInformation": "0.0",
        "safetyCheckDate": null,
        "tachographTestDate": null,
        "gb1": "Gerüstbau",
        "ownerId": null,
        "userId": null,
        "externalId": "",
        "vin": "",
        "labelIds": null,
        "bleGroupEnum": null,
        "profilePictureUrl": "https://api.baubuddy.de/dev/infomaterial/Dokumente_vero_test/RNR_10/Bilder/IMG_20180120_0953251318581889.jpg",
        "thumbPathUrl": "https://api.baubuddy.de/dev/infomaterial/Dokumente_vero_test/RNR_10/Bilder/Thumbs/IMG_20180120_0953251318581889.jpg"
    },
    ...
    ]
    
    
    """

    mock_data = {
    "rnr": "108",
    "gruppe": "Werkzeuge",
    "kurzname": "Makita DTW 190 Akkuschlagschrauber",
    "langtext": "",
    "info": "",
    "sort": "0",
    "lagerort": "Lager Werkzeuge",
    "lteartikel": "Akku Schlagbohrschra",
    "businessUnit": "Gerüstbau",
    "vondat": "2023-10-10",
    "bisdat": None,
    "hu": "2025-10-31",
    "asu": None,
    "createdOn": "2023-10-10",
    "editedOn": "2023-10-12T10:21:49Z",
    "fuelConsumption": "0.0",
    "priceInformation": "0.0",
    "safetyCheckDate": None,
    "tachographTestDate": None,
    "gb1": "Gerüstbau",
    "ownerId": None,
    "userId": None,
    "externalId": "",
    "vin": "",
    "labelIds": "76,132,121",
    "bleGroupEnum": None,
    "profilePictureUrl": "https://api.baubuddy.de/dev/infomaterial/Dokumente_vero_test/RNR_108/Bilder/2023-10-10_04-52-06-1000005472-209-108-1000005472.jpg",
    "thumbPathUrl": "https://api.baubuddy.de/dev/infomaterial/Dokumente_vero_test/RNR_108/Bilder/Thumbs/2023-10-10_04-52-06-1000005472-209-108-1000005472.jpg"
}
    
    
    # Check if the request was successful
    if response.status_code == 200:
        # Convert the response to JSON

        #data= [mock_data]
        data = response.json()

        # Convert the JSON data to a DataFrame
        api_data = pd.DataFrame(data)
    else:
        print(f"/dev/index.php/v1/vehicles/select/active Error: Server returned status code {response.status_code}")


    # Merge CSV data and API data
    merged_data = pd.concat([csv_data, api_data], ignore_index=True)

    # Drop duplicate rows
    merged_data.drop_duplicates(inplace=True)


    # Filter out resources without 'hu'
    if 'hu' in merged_data.columns:
        merged_data = merged_data[merged_data['hu'].notna()]
    else :
        print("Error: 'hu' column not found")


    # Resolve 'colorCode' for each 'labelId'
    if 'labelIds' in merged_data.columns:
        colorCodes = []  # Initialize an empty list to store the color codes
        for index, row in merged_data.iterrows():
            if row['labelIds'] is None:
                continue
            labelIds = row['labelIds'].split(',')  # Split the 'labelIds' string into a list
            for labelId in labelIds:
                response = requests.get(f'https://api.baubuddy.de/dev/index.php/v1/labels/{labelId}', headers=headers)

                '''
                Response format:
                        [
                            {
                                    "id": 134,
                                    "enum": "Werkzeuge",
                                    "displayText": "Werkzeuge",
                                    "colorCode": "",
                                    "baseEntity": "resources",
                                    "isAbstract": false,
                                    "children": [
                                        {
                                            "id": 133,
                                            "parentId": 134,
                                            "enum": "Akkuschrauber",
                                            "displayText": "Akkuschrauber",
                                            "colorCode": "#ff9800",
                                            "baseEntity": "resources"
                                        }
                                    ]
                                }
                            ]
                                            
                
                '''
                
                if response.status_code == 200:
                    response_data = response.json()
                    if response_data:  # Check if the list is not empty
                        first_dict = response_data[0]  # Access the first dictionary in the list
                        colorCode = first_dict.get('colorCode')  # Get the 'colorCode'
                        colorCodes.append(colorCode)  # Add the color code to the list
                    else:
                        print(f"Error: No data returned for label ID {labelId}")
        if colorCodes != []:
            merged_data['colorCodes'] = None
            merged_data.at[index, 'colorCodes'] = colorCodes  # Assign the list of color codes to the 'colorCodes' column    
    else:
        print("Error: 'labelIds' column not found")

   

    # Return processed data
    return jsonify(merged_data.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(port=5000, debug=True)