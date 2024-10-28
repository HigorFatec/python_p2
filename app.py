from flask import Flask,jsonify,render_template, request, flash, redirect
import json

#CONEXÃO SQL SERVER
import pyodbc
SERVER = '177.47.20.123,1433'
DATABASE = 'db_visual_rodopar'
USERNAME = 'cyber'
PASSWORD = '**********'
connectionString = f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'
conn = pyodbc.connect(connectionString)
#FIM


app = Flask(__name__)
app.config['SECRET_KEY'] = "machado"


@app.route("/")
def home():
    return render_template("html/login.html")

@app.route("/login", methods=["POST"])
def login():
    usuario = request.form.get('nome')
    senha = request.form.get('senha')
    with open('usuarios.json') as usuarios:
        lista = json.load(usuarios)
        cont = 0
        for c in lista:
            cont+=1
            if usuario == c['nome'] and senha == c['senha']:
                return redirect("/home")
            if cont >= len(lista):
                flash('Usuario invalido')
                return redirect("/")
            

@app.route("/home", methods=["GET"])
def homepage():
    return render_template("html/home.html")

@app.route('/sobre')
def sobre():
    return render_template('html/sobre.html')


@app.route("/exibir_dados", methods=["GET"])
def exibir_dados():
    try:
        # Substitua esta consulta pela sua
        query = """
        SELECT (SELECT TOP 1 CODFIL FROM db_visual_rodopar.DBO.RODFIL F WHERE F.CODCGC = B.EMPCGC) [FILIAL RODOPAR] 
        ,B.EMPCGC [CNPJ FILIAL]
        ,B.FORCGC [CNPJ FORNECEDOR]
        ,F.CODCLIFOR [COD. RODOPAR]
        ,B.RAZSOC [RAZAO SOCIAL]
        ,B.DATEMI [EMISSAO]
        ,B.DATVEN [VENCIMENTO]
        ,B.VLRTIT [TITULO]
        ,B.NUMDOC [DOCUMENTO]
        ,B.LINDIG [LINHA DIGITAVEL]
        ,P.LINDIG [LINHA DIG. RODOPAR]
        ,IIF(P.ID_PAGDOCI IS NOT NULL,'OK','NAO LOCALIZADO') [LANCADO RODOPAR]
        ,P.NUMDOC [DOCUMENTO RODOPAR]
        ,P.SERIE [SERIE]
        ,P.NUMPAR [PARCELA]

        FROM CargoPoloTemp.dbo.BASEDDA B

        LEFT OUTER JOIN db_visual_rodopar.dbo.RODCLI F ON F.CODCGC = B.FORCGC
        INNER JOIN db_visual_rodopar.dbo.PAGDOCI P ON P.CODCLIFOR = F.CODCLIFOR AND P.DATVEN = B.DATVEN AND P.VLRPAR = B.VLRTIT and p.situac not in ('C','I','L')
        """

        # Executar a consulta
        cursor = conn.cursor()
        cursor.execute(query)

        # Obter os resultados em um dicionário
        columns = [column[0] for column in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # Fechar o cursor
        cursor.close()
        

        # Retornar os resultados como JSON
        #return jsonify({"status": "success", "data": data})

        return render_template("exibir_dados.html", data=data)
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
   # finally:
        # Certifique-se de fechar a conexão
        #conn.close()

@app.route("/executar_comando", methods=["POST"])
def executar_comando():
    try:
        data = request.json
        cnpj_filial = data.get('cnpj_filial')
        cod_rodopar = data.get('cod_rodopar')
        doc_rodopar = data.get('doc_rodopar')
        serie = data.get('serie')
        parcela = data.get('parcela')
    
        print('\n')
        print(f'cnpj_filial:{cnpj_filial}, cod_rodopar:{cod_rodopar}, doc_rodopar:{doc_rodopar}, serie:{serie}, parcela:{parcela}')

        print('\n')
    

        # Sua instrução SQL aqui
        consulta_sql = f"""
            update i set i.lindig = b.lindig
            from pagdoci i
            LEFT OUTER JOIN RODCLI F ON F.codclifor = i.codclifor
            left outer join CargoPoloTemp.dbo.BASEDDA B on b.FORCGC = f.CODCGC and I.DATVEN = B.DATVEN AND i.VLRPAR = B.VLRTIT
            where i.codclifor = {cod_rodopar} and i.numdoc = '{doc_rodopar}' and i.SERIE = '{serie}' and i.numpar = {parcela}
 
        """

        # Execute a consulta SQL usando o cursor do banco de dados
        cursor = conn.cursor()
        cursor.execute(consulta_sql)
        cursor.commit()

        return jsonify({"status": "success", "message": "Comando executado com sucesso"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    
    finally:
        cursor.close()



if __name__  == "__main__":
    app.run(host= '10.1.1.114', port=5000 ,debug=True)