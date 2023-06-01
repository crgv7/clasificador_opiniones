#Libreria para Scrapper web
import html
from requests_html import HTMLSession
from bs4 import BeautifulSoup
#-----------------------------------------

# librerias para Procesamineto de datos
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import nltk
import cleantext
#---------------------------------------------------

#intalar librerias para clasificador de texto
from cleantext import clean
from pysentimiento import create_analyzer
#---------------------------------------------------------

#libreria para pyqt5
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication,QTableWidget,QTableWidgetItem,QComboBox,QMessageBox
#---------------------------------------------------------------------------------------------
#se declaran esta variables aqui pq mas tarde se usaran como global
datos = pd.DataFrame({})
posdf = pd.DataFrame({})
negdf = pd.DataFrame({})
neudf = pd.DataFrame({})
hay_datos=False
class GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("GUI.ui",self)
        self.scanbtn.clicked.connect(self.fn_scan)
        self.guardarbtn.clicked.connect(self.guardar)
        self.graficarbtn.clicked.connect(self.graficar)
       
        self.comboBox.activated[str].connect(self.handleActivated)  
      
    def fn_scan(self):
          
        text=self.url.text()
        if len(text)!=0:
            text2=text[0:64]
            text3=text[64:len(text)]
        
            self.tabla.setRowCount(5)
            print("este el texto"+ text)
        
        #hacer scrapping web, extraer comentarios y guardarlos en un archivo de texto
         
            num=0
            review=""
            i=0 
            y=13 # cantidad de iteraciones

            with open('datasets.txt', 'w') as f: # crear archivo dataset.txt
                session = HTMLSession() #hacer peticion para extraer comentarios de tripAdvisor
                
                while i<=y: #Va a iterar 13 veces sobre la pagina y como la pagina muestra de 5 en 5 comentarios, extrae 65 comentarios 
                    try:
                        #Ahora se ingresa la url del hotel 
                        url=text2+review+text3
                        #url=f"https://www.tripadvisor.es/Hotel_Review-g445055-d1165746-Reviews{review}-Hotel_Royalton-Bayamo_Granma_Province_Cuba.html"
                        print(url)
                        html_text2 = session.get(url)
                        print("hize request")
                        soup=BeautifulSoup(html_text2.html.html, 'lxml')
                        coments=soup.find_all('span', class_='QewHA H4 _a')# guardar comentarios en la variable coments
                        num=num+5
                        i=i+1
                        review=f"-or{num}"
 
                        for coment in coments:
                            print("entre al for")
                            #Cada comentario lo escribe en el archivo
                            f.write(coment.text+'\n')  
                                
  
                    except:
                        print('se revisaron todos los comentarios') 
                print("terminada la extraccion")  
                
            #Leer dataset     
            df=pd.read_csv('datasets.txt', delimiter='\t', names=['texto'],encoding='latin-1')#guardar textos en un dataframe
            df = df.reset_index()#asignar index            
            #Crear analizador
            analyzer = create_analyzer(task="sentiment", lang="es")
            res={}
            for index, row in df.iterrows():  
                #use cleantext para procesar las opiniones, debo probar todavia si es necesario, usar el procesamiento de texto para este caso dependiendo de los resultados  
                clean_text = clean(row['texto'], stemming=True ,extra_spaces=True, stopwords=True, lowercase=True,stp_lang='spanish',punct=True)
                out=analyzer.predict(clean_text)#clasifica el texto
                res[index]=out.output

            print(res)
       #-------------------------------------------------------------------------------------------------------------------

            #trabajando con el dataframe
            frame=pd.DataFrame( {'clasificacion': res})#crear nuevo dataframe con una columna de clasificacion
            frame=frame.reset_index()# asignar index
            frame.columns
            global datos
            datos = frame.merge(df, how='left') #unir dataframes, df a frame, a cada texto se le asigna su clasificacion
            #datos['clasificacion'].replace('NEU', 'POS', inplace=True)#se toman lo clasicados en neutro como positivos
        
            # creando dataframe para posdf, negdf, neudf
            global negdf,posdf,neudf 
            posdf=datos[datos['clasificacion'] == 'POS']
            negdf=datos[datos['clasificacion'] == 'NEG']
            neudf=datos[datos['clasificacion'] == 'NEU']
            #llenar tabla y ajustar tabla
            self.tabla.setRowCount(datos.shape[0])
            for row in range(datos.shape[0]):
                for col in range(datos.shape[1]):
                    self.tabla.setItem(row, col, QTableWidgetItem(str(datos.iat[row,col])))
            self.tabla.resizeRowsToContents() 
            self.tabla.setColumnWidth(0,50)  
            self.tabla.setColumnWidth(1,50)  
            self.tabla.setColumnWidth(2,350)  
            self.tabla.verticalHeader().hide()
          
            for i in range(datos.shape[0]):
                self.tabla.setRowHeight(i, 100)   
            
            global hay_datos    
            hay_datos=True             
        else:
            QMessageBox.information(None, 'Error', 'Campo vacio')
                            
        #-------------------------------------------------------------------------------------------------------------------------------
        # empezar a trabajar con dataframe
          

        #---------------------------------------------------------------------------------------------------------------------
        #------------------------------------------------------------------------------------------------------------------------

    # funcion de filtrado
    def handleActivated(self, text):
        # Función que maneja la opción seleccionada
        if text == "positivos":
            print(posdf.shape)
            print(type(posdf))
              #llenar tabla y ajustar tabla
            self.tabla.setRowCount(posdf.shape[0])
            for row in range(posdf.shape[0]):
                for col in range(posdf.shape[1]):
                    self.tabla.setItem(row, col, QTableWidgetItem(str(posdf.iat[row,col])))
            self.tabla.resizeRowsToContents() 
            self.tabla.setColumnWidth(0,50)  
            self.tabla.setColumnWidth(1,50)  
            self.tabla.setColumnWidth(2,350)  
            self.tabla.verticalHeader().hide()
          
            for i in range(posdf.shape[0]):
                self.tabla.setRowHeight(i, 100)    
            
        elif text == "negativos":
            #llenar tabla y ajustar tabla
            self.tabla.setRowCount(negdf.shape[0])
            for row in range(negdf.shape[0]):
                for col in range(negdf.shape[1]):
                    self.tabla.setItem(row, col, QTableWidgetItem(str(negdf.iat[row,col])))
            self.tabla.resizeRowsToContents() 
            self.tabla.setColumnWidth(0,50)  
            self.tabla.setColumnWidth(1,50)  
            self.tabla.setColumnWidth(2,350)  
            self.tabla.verticalHeader().hide()  
                
            for i in range(negdf.shape[0]):
                self.tabla.setRowHeight(i, 100)  
                  
        elif text == "neutrales":
              #llenar tabla y ajustar tabla
            self.tabla.setRowCount(neudf.shape[0])
            for row in range(neudf.shape[0]):
                for col in range(neudf.shape[1]):
                    self.tabla.setItem(row, col, QTableWidgetItem(str(neudf.iat[row,col])))
            self.tabla.resizeRowsToContents() 
            self.tabla.setColumnWidth(0,50)  
            self.tabla.setColumnWidth(1,50)  
            self.tabla.setColumnWidth(2,350)  
            self.tabla.verticalHeader().hide()
          
            for i in range(neudf.shape[0]):
                self.tabla.setRowHeight(i, 100)    
                  
    def guardar(self):
        if hay_datos==True:
            # Guardar el DataFrame en un archivo CSV
            datos.to_csv('datos_clasificados.csv', index=False)
        else:
             QMessageBox.information(None, 'Error', 'No hay datos')
  #Graficar resultados           
    def graficar(self):
        if hay_datos==True:
            # graficar resultados
            pos=datos['clasificacion'].eq("POS").sum()
            neg=datos['clasificacion'].eq("NEG").sum()
            neu=datos['clasificacion'].eq("NEU").sum()
            resultados = [pos,neg,neu]
            clasificacion = ["POSITIVOS","NEGATIVO","NEUTRAL"]
            plt.pie(resultados, labels=clasificacion,autopct='%1.1f%%')
            plt.show()
        else:
            QMessageBox.information(None, 'Error', 'No hay datos')

    
    
    
    
if __name__=="__main__":
    app=QApplication(sys.argv)
    gui=GUI()
    gui.show()
    sys.exit(app.exec_())   
    
        
    # end def
    