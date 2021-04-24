Sovelluksen ominaisuuksia:

* Käyttäjä voi kirjautua sisään ja ulos sekä luoda uuden tunnuksen.
* Opiskelija näkee listan kursseista ja voi liittyä kurssille.
* Opiskelija voi lukea kurssin tekstimateriaalia sekä ratkoa kurssin tehtäviä.
* Opiskelija pystyy näkemään tilaston, mitkä kurssin tehtävät hän on ratkonut.
* Opettaja pystyy luomaan uuden kurssin, muuttamaan olemassa olevaa kurssia ja poistamaan kurssin.
* Opettaja pystyy lisäämään kurssille tekstimateriaalia ja tehtäviä. Tehtävä voi olla ainakin monivalinta tai tekstikenttä, johon tulee kirjoittaa oikea vastaus.
* Opettaja pystyy näkemään kurssistaan tilaston, keitä opiskelijoita on kurssilla ja mitkä kurssin tehtävät kukin on ratkonut.


# Välipalautus 3

Sovelluksen koodi on nyt jaoteltu omiin kansioihin ja ulkoasua paranneltu selkeämmäksi, lisäksi sovellus antaa käyttäjälle ilmoituksen nyt mm. onnistuneista tehtävien ratkaisuista, uuden tunnuksen luomisesta, kurssin luomisesta jne. Tyhjät syötteet tarkistetaan aiempaa paremmin eikä sql kyselyitä ajeta jos käyttäjä ei ole kirjautunut sisälle (tämän voisi varmasti suorittaa fiksumminkin, jostain syystä yksi metodi tähän ei toiminut). Sovelluksen saaminen silmää miellyttäväksi olikin yllättävän haastavaa, tässä riittää vielä hiottavaa.

Heroku toimi testatessa chromella huonosti, safarilla ja omalla koneella hyvin. Perustoimintoihin ei sinänsä ole tehty muutoksia edellisen kerran jälkeen, joten edellisen kerran kuvaus pitää niiden osalta edelleen paikkansa.

# Välipalautus 2   10.4


Sovelluksen runko ja aiemmin kuvatut toiminnot ovat pääosin valmiita, toiminnoissa on kuitenkin vielä jonkin verran puutteita ja koodi vaatii paljon siistimistä.
Korjattavaa seuraavaa palautusta varten:
* Tyhjien syötteiden tarkastus
* Tiettyjen muuttujien nimeäminen loogisemmin ja yhdenmukaisemmin
* Tarkistusten lisäys, jotta tietokantaan ei lisätä samaa tietoa vahingossa useampaan kertaan
* Ulkoasun muokkaus siedettäväksi
* Toimintojen jaottelu kansioihin ja refraktointi
* Vikakoodin näyttäminen, jos käyttäjä tekee jotain tyhmää
* Sovellus ei toistaiseksi ilmoita myöskään tehtävän oikeasta ratkaisusta muuten kuin päivittämällä ratkaistujen tehtävien määrän
* Sovellus ei kerro oppilaalle onnistuneesta kurssi-ilmoittautumisesta

[Heroku](http://moodle-lite.herokuapp.com/)

Sovellukseen voi kirjautua nyt luomalla uuden tunnuksen (rooli automaattisesti student) tai opettajana; tunnus: Opettaja1 salasana: ope1. Roolin muutos toistaiseksi vain suoraan tietokannan kautta. 

Opettaja voi luoda uuden kurssin ja lisätä tai poistaa materiaalia tai koko kurssin. Opettaja ei voi ratkoa tehtäviä, mutta näkee ne. Monivalinnan luomisen yhteydessä opettaja merkitsee halutut oikeat vastaukset, sovellus ei tarkasta tällä hetkellä tyhjiä rivejä. Klikkaamalla linkistä "oppilaat" opettaja näkee kurssin osallisujat (toistaiseksi yksi henkilö voi ilmoittautua useaan kertaan) ja tehdyt tehtävät.

Oppilas näkee listan kaikista kursseista ja voi liittyä niille, klikkaamalla kurssia oppilas näkee listan tehtävistä ja kurssin materiaalin. Monivalinnat ratkotaan klikkaamalla oikeat vastaukset, vapaan tekstin tehtävä vaatii täsmälleen oikean syötteen.
