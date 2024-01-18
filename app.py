from flask import Flask, jsonify, request
import json
import pandas as pd
import math
from flask_cors import CORS, cross_origin



def calculo_prev(*tuplas, n_propie, cuota):

    tuplas = sorted(tuplas, key=lambda x: x[0])

    variables = [[] for _ in range(len(tuplas))]

    # Itera sobre los elementos de las tuplas
    for i in range(len(tuplas[0])):
        valores = [t[i] for t in tuplas]

        for j, valor in enumerate(valores):
            variables[j].append(valor)

    #Obtencion de meses maximo
    total_meses = 0
    suple_var = 0
    periodos = []
    for var in variables:
        periodos.append(var[0])
        if var[0] > total_meses:
            total_meses = var[0]
    
    
    #Cuota por meses
    gasto_x_mes = []
    for i in range(total_meses):
        for var in variables:
            if i < var[0]:
                spl = round((var[1]/var[0])/n_propie, 2)
                suple_var += spl
        gasto_x_mes.append(suple_var)
        suple_var = 0
    
    #Resultado
    cuotas_total = []
    
    for i in periodos:
        cuotas_total.append(math.ceil(gasto_x_mes[i -1] + cuota))

    return sum(cuotas_total)


app = Flask(__name__)
cors = CORS(app)


@app.route('/', methods=['GET'])
def Hello():
    return """<h1>API para cuota de administracion</h1>
    <br>
    https://api-tripu-dev-zgtp.1.us-1.fl0.io/calculo/
    <br>
    <br>
    GASTOS PREVISTOS:
    {
    "tuplas": [
        {"años": 5, "monto": 3000},
        {"años": 7, "monto": 1500}
    ]
    }
    <br>
    Devuelve la cantidad que tiene que pagar cada vecino según su coeficiente para cada uno de los pagos previstos introducidos (en el orden introducido).
    Devolverá algo parecido a esto: 
    <br>
    {
        "cuotas_vecino": [
            70.0,
            50.71
        ],
        "cuotas_vecino_con_atico": [
            230.0,
            133.57
        ],
        "cuotas_vecino_con_bajo": [
            170.0,
            112.14
        ]
    }"""


@app.route('/calculadora', methods=['GET','POST'])
@cross_origin(origin="http://localhost:5173")
def suma():

    data = request.json

    cuota_actual = data['cuota']
    n_propie = data['n_propietarios']
    ahorro = data['ahorro']
    fondos_iniciales = data['fondos']
    anios = data['anios']

    tiempo = anios * 12
    gasto_real = ahorro - fondos_iniciales 
    suplemento = (gasto_real / tiempo) / n_propie
    resultado = cuota_actual + suplemento

    return jsonify({'Nueva cuota': resultado})


@app.route('/calculadora_previ', methods=['GET','POST'])
@cross_origin(origin="http://localhost:5173")
def calculadora_prevision():

    data = request.json

    tuplas = [(item['años'], item['monto']) for item in data.get('tuplas', [])]
    n_propie = int(data['n_propietarios'])
    cuota = int(data['cuota'])

    output = calculo_prev(*tuplas, n_propie=n_propie, cuota=cuota)
    output  = math.ceil(sum(output)/len(output))

    return jsonify({'Nueva/s cuota/s': output})


if __name__ == "__main__":
    app.run(debug=True, port=8000)