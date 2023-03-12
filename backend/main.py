from flask import Flask, jsonify, request
import pandas as pd
from pandas.io.json import json_normalize
import requests
from tabulate import tabulate
from sklearn.cluster import KMeans

app = Flask(__name__)
apiKey = "uJHMEjeagmFGldXp661-pDMf4R-PxvWIu7I68UjYC5Q"


@app.route('/Locations/<float:position_latitude>/<float:position_longitude>')
def map_clusters(position_latitude, position_longitude):
    url = f'https://discover.search.hereapi.com/v1/discover?in=circle:{position_latitude},{position_longitude};r=10000&q=apartment&apiKey={apiKey}'
    data = requests.get(url).json()
    # # Cleaning API data
    d2 = {}
    d2['items'] = []
    for item in data['items']:
        address = item['address']
        label = address['label']
        d2['items'].append(
            {'title': item['title'], 'label': label, 'distance': item['distance'], 'access': item['access'], 'position.lat': item['position']['lat'], 'position.lng': item['position']['lng'], 'address.postalCode': item['address']['postalCode'], 'id': item['id']})
    # # Counting no. of cafes, department stores and gyms
    # df_final = d2[['position.lat', 'position.lng']]
    total = 0
    CafeList = []
    DepList = []
    GymList = []
    longitudes = []
    latitudes = []
    for item in d2["items"]:
        latitudes.append(item["position.lat"])
        longitudes.append(item["position.lng"])

    for lat, lng in zip(latitudes, longitudes):
        total = total+1
        radius = '1000'  # Set the radius to 1000 metres
        latitude = lat
        longitude = lng

        search_query = 'cafe'  # Search for any cafes
        url = f'https://discover.search.hereapi.com/v1/discover?in=circle:{latitude},{longitude};r={radius}&q={search_query}&apiKey={apiKey}'
        results = requests.get(url).json()
        venues = pd.json_normalize(results['items'])
        if (len(results['items']) == 0):
            CafeList.append(0)
            continue
        CafeList.append(int(venues['title'].count()))

        search_query = 'gym'  # Search for any gyms
        url = f'https://discover.search.hereapi.com/v1/discover?in=circle:{latitude},{longitude};r={radius}&q={search_query}&apiKey={apiKey}'
        results = requests.get(url).json()
        venues = pd.json_normalize(results['items'])
        if (len(results['items']) == 0):
            GymList.append(0)
            continue
        GymList.append(int(venues['title'].count()))

        search_query = 'department-store'  # search for supermarkets
        url = f'https://discover.search.hereapi.com/v1/discover?in=circle:{latitude},{longitude};r={radius}&q={search_query}&apiKey={apiKey}'
        results = requests.get(url).json()
        venues = pd.json_normalize(results['items'])
        if (len(results['items']) == 0):
            DepList.append(0)
            continue
        DepList.append(int(venues['title'].count()))

    if (total != len(CafeList)):
        u = len(CafeList)
        while (u != total):
            u = u+1
            CafeList.append(0)

    if (total != len(GymList)):
        u = len(GymList)
        while (u != total):
            u = u+1
            GymList.append(0)

    if (total != len(DepList)):
        u = len(DepList)
        while (u != total):
            u = u+1
            DepList.append(0)
    df_final = {
        'position.lat': latitudes,
        'position.lng': longitudes,
        'cafe': CafeList,
        'Department Stores': DepList,
        'Gyms': GymList
    }

    # # Run K-means clustering on dataframe
    kclusters = 3

    data = [[lat for lat in df_final['position.lat']],
            [lng for lng in df_final['position.lng']],
            [cafe for cafe in df_final['cafe']],
            [ds for ds in df_final['Department Stores']],
            [gym for gym in df_final['Gyms']]]

    print(data)

    # Converting the 2d Lists into dataframe (each row for contains data for particular location)
    finalList = []
    for i in range(0, len(data[0])):
        finalList.append([data[0][i], data[1][i], data[2]
                          [i], data[3][i], data[4][i]])

    df = pd.DataFrame(finalList, columns=[
                      'position.lat', 'position.lng', 'Cafes', 'Department Stores', 'Gyms'])
    print(df)

    # applying kmeans clustering
    kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(df)
    cluster = [int(x) for x in kmeans.labels_]
    df_final['Cluster'] = cluster

    # data = [[lat for lat in df_final['position.lat']],
    #         [lng for lng in df_final['position.lng']],
    #         [cafe for cafe in df_final['cafe']],
    #         [ds for ds in df_final['Department Stores']],
    #         [gym for gym in df_final['Gyms']],
    #         [cluster for cluster in df_final['Cluster']]]
    # finalList = []
    # for i in range(0, len(data[0])):
    #     finalList.append([data[0][i], data[1][i], data[2][i],
    #                      data[3][i], data[4][i], data[5][i]])

    # df = pd.DataFrame(finalList, columns=[
    #                   'position.lat', 'position.lng', 'Cafes', 'Department Stores', 'Gyms', 'Cluster'])

    # print(df)

    return df_final


if __name__ == '__main__':
    app.run(debug=True)
