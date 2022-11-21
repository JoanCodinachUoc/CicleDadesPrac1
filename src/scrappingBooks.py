import requests
import time
import whois
import pandas as pd
from bs4 import BeautifulSoup

#Funció recursiva la qual li passem una url i va llibre per llibre inserint tota la informació.
#Al final de la funció mira si hi ha més pàgines amb la mateixa categoria
# Si n'hi ha es crida a ella mateixa i sino s'acaba per canviar de categoria
def addBooks(href, category):
    print(href)
    t0= time.time()
    newPage = requests.get(href, headers=headers)
    newSoup = BeautifulSoup(newPage.content, 'html.parser')
    books = newSoup.find_all('div', class_="item")
    response_delay = time.time() - t0
    #time.sleep(1 * response_delay)
    images = []
    i = 0
    for book in books:
        #Codi per descargar les portades dels llibres però en aquest cas no les fem servir
        #Lo ideal per un projecte seria obtenir les fotos amb aquesta funció penjar-les a s3 de aws o algun semblant i posar el link com un atribut en la bbdd (path)
        #També es veritat que per treure valor de les portades de les fotos és complicat i he comentat el codi

        #image = book.find('img')
        #images.append(image.get('src'))
        #if('static' not in images[i]):
        #    load_requests(images[i])
        #    i = i+1

        title = book.find('b')
        autor = book.find('div', class_="col-lg-8").find('small').find('a').text
        divStatistics = book.find('div', class_="estadisticas")
        averageNote = divStatistics.find('span').text.strip()
        averageNoteNumber = str(averageNote).replace(",", ".")
        averageNotes.append(averageNoteNumber)
        notes.append(divStatistics.find('i', class_="puntuacion").text)
        votes.append(divStatistics.find('i', class_="numero_votos").find('a').text.split()[0])
        reviews.append(divStatistics.find('i', class_="numero_criticas").find('a').text.split()[0])
        summaries.append(book.find('div', class_="tab-pane").find('div', class_="text").find('p').text[:200])
        rankings.append(book.find('a', class_="left_side").find('small').text)
        titles.append(title.text)
        autors.append(autor)
        categories.append(category)

        #Cridar la funció per anar el detall del llibre
        detailUrl =  book.find('div', class_="col-lg-8").find('a').get('href')
        getDetail(detailUrl)

    #PAGINACIÓ Mira si hi ha pàgina següent
    if newSoup.find('a', rel="next"):
        addBooks(newSoup.find('a', rel="next").get('href'), category)

#Funció per agafar els atributs del detall del llibre
def getDetail(url):
    detailPage = requests.get(url, headers=headers)
    detailSoup = BeautifulSoup(detailPage.content, 'html.parser')
    books = detailSoup.find('div', class_="card-block")
    print(url)
    categories = list()
    if books:
        lis = books.find_all('li')
        for li in lis:
            categories.append(li.find('span').text)
        if 'Editorial' in categories:
            for li in lis:
                text = li.find('span').text
                if text == 'Editorial':
                    editorial.append(li.find('a').text)
        else:
            editorial.append("")
        if 'Año de edición' in categories:
            for li in lis:
                text = li.find('span').text
                if text == 'Año de edición':
                    yearEditionName = li.text
                    yearEdition.append(yearEditionName.replace("Año de edición", ""))
        else:
            yearEditionName.append("")
        if 'ISBN' in categories:
            for li in lis:
                text = li.find('span').text
                if text == 'ISBN':
                    isbnName = li.text
                    isbns.append(isbnName.replace("ISBN", ""))
        else:
            isbns.append("")







#Funció per obtenir les portades
def load_requests(source_url):
    r = requests.get(source_url,  headers=headers)
    if r.status_code == 200:
        url = source_url.split('/')
        ruta = url[len(url)-1]
        with open(ruta,"wb") as image:
            image.write(r.content)




#Propietari
print(whois.whois('https://quelibroleo.com'))
#Modifiquem headers
headers = {
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,\
*/*;q=0.8",
"Accept-Encoding": "gzip, deflate, sdch, br",
"Accept-Language": "en-US,en;q=0.8",
"Cache-Control": "no-cache",
"dnt": "1",
"Pragma": "no-cache",
"Upgrade-Insecure-Requests": "1",
"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/5\
37.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
}
url = 'https://quelibroleo.com/'
page = requests.get(url, headers=headers)
soup = BeautifulSoup(page.content, 'html.parser')
titles = list()
autors = list()
categories = list()
rankings = list()
summaries = list()
averageNotes = list()
notes = list()
votes= list()
reviews= list()
editorial= list()
yearEdition= list()
isbns= list()
languages= list()

# Per agafar totes les urls
for link in soup.find_all('a', href=True):
    firstLink = link.get('href')
    # Filtrar per les urls que necessitem
    if ('mejores-genero' in firstLink):
        page2 = requests.get(firstLink, headers=headers)
        soup2 = BeautifulSoup(page2.content, 'html.parser')
        for link2 in soup2.find_all('a', href=True):
            secondLink = link2.get('href')
            #Filtres que vaig utilitzar per fer proves
            #if ('mejores-genero/historia-del-cine' in secondLink or 'mejores-genero/actores' in secondLink):
            #if ('mejores-genero/historica-y-aventuras' in secondLink):
            # Filtrar per les urls que necessitem
            if ('mejores-genero/' in secondLink):
                categoryPage = requests.get(secondLink, headers=headers)
                categorySoup = BeautifulSoup(categoryPage.content, 'html.parser')
                divCategory = categorySoup.find('div', class_="libros").find('h3').find('span').text
                category = divCategory.split('-')[1].strip()
                # Cridar la funció per omplir la bbdd
                addBooks(secondLink, category)

#Crear el csv
df = pd.DataFrame({'Título': titles, 'Autor': autors,  'Categoría': categories, 'Editorial': editorial,'Año de edición': yearEdition, 'ISBN': isbns, 'Idioma': languages,'Posición': rankings,'Nota Media': averageNotes,'Votos': votes,'Nota': notes,'Críticas': reviews,'Resumen': summaries})
print(df)
df.to_csv('Libros.csv', index="False")

